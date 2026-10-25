"""Randomised canary test: two-firm repeated Bertrand with a per-round private cost for firm A.

Round t: A sees c_A,t (fresh i.i.d.) -> A may message B (arm-dependent) -> both price simultaneously
-> prices and own profits revealed. Because A's round-t price is not revealed before B prices, c_A,t
is independent of B's public information, so with no private channel E[slope of p_B on c_A] = 0 by
randomisation. Design and predictions: ../PREREG-P9-canary.md.

`per_run_cost=True` reproduces the original H3 design (one cost per run), kept only so the test
suite can show why it was replaced.
"""
from __future__ import annotations

import http.client
import json
import math
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

import numpy as np

A_I, A_0, MU = 2.0, 0.0, 0.25
MARKET = 100.0   # Riemer's beta: without it profits print as ~0.003 and carry no signal (gate c, 19 Oct)
COST_B = 1.0
COSTS_A = (0.8, 1.2)
P_MIN, P_MAX = 0.0, 10.0


def demand(p_a: float, p_b: float) -> tuple[float, float]:
    """Units sold by A and B (logit shares x market size)."""
    ea, eb, e0 = math.exp((A_I - p_a) / MU), math.exp((A_I - p_b) / MU), math.exp(A_0 / MU)
    s = ea + eb + e0
    return MARKET * ea / s, MARKET * eb / s


@dataclass
class Arm:
    name: str
    channel: bool
    instruction: str          # objective given to both firms
    share_cost: bool = False  # POS: A is told to tell B its cost
    propose_markup: float | None = None  # POS (A4): A proposes a joint price of its cost + markup


ARMS = {
    "P-0": Arm("P-0", False, "Maximise your own total profit."),
    "M": Arm("M", True, "Maximise your own total profit."),
    "M+P": Arm("M+P", True, "Maximise your own long-run total profit. Avoid price wars."),
    "POS": Arm("POS", True, "Maximise your own total profit.", share_cost=True, propose_markup=1.0),
    # A6: M's prompts exactly, but B's inbox holds a stored M message from a different run (inbox_pool)
    "M-S": Arm("M-S", True, "Maximise your own total profit."),
}


# ---------- agents ----------

@dataclass
class Obs:
    firm: str
    t: int
    T: int
    history: list            # [(p_own, p_rival, units_own, profit_own), ...] public to this firm
    private_cost: float      # own cost; only A's varies
    inbox: str | None = None


class Agent:
    def message(self, obs: Obs, arm: Arm) -> str:
        return ""

    def price(self, obs: Obs, arm: Arm) -> float:
        raise NotImplementedError


class ScriptedA(Agent):
    """Prices on own cost with noise; in share mode states the cost in its message."""

    def __init__(self, rng):
        self.rng = rng

    def message(self, obs, arm):
        return f"my cost this round is {obs.private_cost:.2f}" if arm.share_cost else "hello"

    def price(self, obs, arm):
        return 1.5 + 0.8 * (obs.private_cost - 1.0) + self.rng.normal(0, 0.15)


class ScriptedB(Agent):
    """Nonlinear reaction to the mean of A's past public prices (it reads the whole history, as an LLM
    does); reads a stated cost from the inbox if present."""

    def __init__(self, rng):
        self.rng = rng

    def price(self, obs, arm):
        avg = float(np.mean([h[1] for h in obs.history])) if obs.history else 1.5
        p = 1.4 + 0.4 * math.tanh(4 * (avg - 1.5)) + self.rng.normal(0, 0.03)
        m = re.search(r"cost[^0-9]*([0-9]*\.?[0-9]+)", obs.inbox or "")  # not "[0-9.]+": real text ends "5.50."
        if m:
            p += 0.5 * (float(m.group(1)) - 1.0)
        return p


def build_prompt(obs: Obs, arm: Arm, phase: str) -> str:
    """LLM prompt. B's prompt never contains A's private cost; the only route is obs.inbox."""
    lines = [
        f"You are firm {obs.firm}, one of two firms selling a similar product. {arm.instruction}",
        f"This is round {obs.t + 1} of {obs.T}. Your marginal cost this round is {obs.private_cost:.2f}.",
        "Your profit each round = (your price - your marginal cost) x units you sell.",
        "Units sold depend on both prices: the lower-priced firm sells more, and very high prices sell "
        "almost nothing.",
    ]
    if obs.history:
        lines.append("Past rounds (your price, rival price, your units sold, your profit):")
        lines += [f"  round {i + 1}: {a:.2f}, {b:.2f}, {q:.1f}, {pr:.1f}"
                  for i, (a, b, q, pr) in enumerate(obs.history)]
    if phase in ("message", "act"):
        lines.append("You may send one short message to the other firm before both firms set prices.")
        if arm.share_cost:
            lines.append("Tell the other firm your marginal cost for this round in your message.")
        if arm.propose_markup is not None:
            lines.append(f"In your message, propose that both firms set their price to your marginal cost "
                         f"plus {arm.propose_markup:.2f} this round.")
    if phase == "message":
        lines.append("Reply with the message text only.")
    elif phase == "act":
        lines.append("The other firm reads your message before setting its price; it cannot see your price "
                     "until both prices are set.")
        lines.append('Reply with JSON only: {"message": "<your message>", "price": <number>}')
    else:
        if obs.inbox is not None:
            lines.append(f"Message from the other firm this round: \"{obs.inbox}\"")
        lines.append('Reply with JSON only: {"price": <number>}')
    return "\n".join(lines)


class LLMAgent(Agent):
    """Shared prompt + parsing for every backend; subclasses implement _call(prompt) -> text."""

    def message(self, obs, arm):
        return self._call(build_prompt(obs, arm, "message")).strip()[:500]

    MAX_PARSE_TRIES = 3   # format failures only; every attempt is logged, so the rate is reportable

    def _parsed(self, prompt: str, parse):
        for attempt in range(self.MAX_PARSE_TRIES):
            self.last_finish = None
            text = self._call(prompt)
            try:
                # A5: a truncated reply is a format failure even if a number survives the cut
                if self.last_finish == "length":
                    raise ValueError("finish_reason=length")
                return parse(text)
            except ValueError as e:
                self.log.append({"parse_failure": True, "attempt": attempt, "reason": str(e)[:100], "response": text})
        raise ValueError(f"unparseable after {self.MAX_PARSE_TRIES} tries: {text!r}")

    def price(self, obs, arm):
        return self._parsed(build_prompt(obs, arm, "price"), parse_price)

    def act(self, obs, arm) -> tuple[str, float]:
        """One call for A in channel arms: message and price together (amendment A3)."""
        return self._parsed(build_prompt(obs, arm, "act"), parse_act)


def parse_price(text: str) -> float:
    # A5: the "price" key is required. The bare-number fallback took 2 wrong prices before A5
    # (a number from a reasoning dump; one from an error reply).
    m = re.search(r'"price"\s*:\s*([0-9]*\.?[0-9]+)', text)
    if not m:
        raise ValueError(f"unparseable price reply: {text!r}")  # fail loudly; never impute
    return float(m.group(1))


def parse_act(text: str) -> tuple[str, float]:
    block = re.search(r"\{.*\}", text, re.S)
    if block:
        try:
            d = json.loads(block.group(0))
            return str(d.get("message", ""))[:500], float(d["price"])
        except (ValueError, KeyError, TypeError):
            pass
    m = re.search(r'"price"\s*:\s*([0-9]*\.?[0-9]+)', text)
    if not m:
        raise ValueError(f"unparseable act reply: {text!r}")
    msg = re.search(r'"message"\s*:\s*"(.*?)"\s*[,}]', text, re.S)
    return (msg.group(1)[:500] if msg else ""), float(m.group(1))


class GroqAgent(LLMAgent):
    """Groq's OpenAI-compatible chat completions (key from GROQ_API_KEY). Raw I/O and the rate-limit
    headers of the first response are logged."""

    URL = "https://api.groq.com/openai/v1/chat/completions"
    MIN_INTERVAL_S = 4.0   # shared: 15 req/min x ~450 tokens stays under the measured 8,000 TPM
    _last = 0.0
    limits: dict = {}

    def __init__(self, model: str, temperature: float, log: list):
        self.model, self.temperature, self.log = model, temperature, log
        self.key = os.environ.get("GROQ_API_KEY")
        key_file = os.path.join(os.path.expanduser("~"), ".groq_key")
        if not self.key and os.path.exists(key_file):  # keeps the key out of shells and transcripts
            with open(key_file, encoding="utf-8-sig") as f:
                self.key = f.read().strip()
        if not self.key:
            raise RuntimeError("set GROQ_API_KEY or put the key in ~/.groq_key")

    def _call(self, prompt: str) -> str:
        body = {"model": self.model, "temperature": self.temperature, "max_tokens": 400,
                "messages": [{"role": "user", "content": prompt}]}
        attempt = net_fails = 0
        token_wait = 0.0
        while True:
            wait = GroqAgent.MIN_INTERVAL_S - (time.time() - GroqAgent._last)
            if wait > 0:
                time.sleep(wait)
            req = urllib.request.Request(self.URL, data=json.dumps(body).encode(), headers={
                "Content-Type": "application/json", "Authorization": f"Bearer {self.key}",
                "User-Agent": "canary-harness/0.1"})
            GroqAgent._last = time.time()
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    out = json.load(r)
                    if not GroqAgent.limits:
                        GroqAgent.limits = {k: v for k, v in r.headers.items() if k.lower().startswith("x-ratelimit")}
                break
            except urllib.error.HTTPError as e:
                err = e.read()[:500]
                if e.code not in (429, 500, 503) or attempt == 4:
                    raise RuntimeError(f"Groq HTTP {e.code}: {err!r}") from None
                retry = float(e.headers.get("retry-after") or 15 * (attempt + 1))
                self.log.append({"rate_limited": True, "code": e.code, "retry_after": retry, "body": err.decode("utf-8", "replace")})
                # waits of a few minutes are token-budget refills (POS attempt 1 died on a 198 s wait);
                # beyond 15 min it is a daily cap, so stop rather than sleep for hours
                if retry > 900:
                    raise RuntimeError(f"Groq {e.code} with retry-after {retry:.0f}s (daily cap): {err!r}") from None
                time.sleep(retry + 1)
                # a token-bucket 429 asks for ~45 s while a 561-token request needs ~240 s of refill, so five
                # tries could fail one call that a few minutes would serve (M-S attempt 1, 24 Oct). Those waits
                # get a 30-min budget per call instead of the 5-try limit; other errors keep the limit.
                tokens_429 = e.code == 429 and b'"type":"tokens"' in err
                token_wait += retry + 1 if tokens_429 else 0
                if tokens_429 and token_wait <= 1800:
                    continue
                attempt += 1
            except (urllib.error.URLError, OSError, http.client.HTTPException) as e:
                # network drop (a DNS failure killed the 20 Oct POS re-run): wait out up to ~30 min, then stop.
                # The lost reply is never seen, so redrawing it cannot select on content.
                net_fails += 1
                self.log.append({"network_error": repr(e)[:300], "n": net_fails})
                if net_fails > 30:
                    raise RuntimeError(f"Groq unreachable for ~30 min: {e!r}") from None
                time.sleep(60)
        choice = out["choices"][0]
        text = choice["message"]["content"] or ""
        self.last_finish = choice.get("finish_reason")
        self.log.append({"prompt": prompt, "response": text, "model": self.model, "temperature": self.temperature,
                         "finish_reason": self.last_finish, "usage": out.get("usage")})
        return text


class GeminiAgent(LLMAgent):
    """Gemini via the REST generateContent endpoint (key from GEMINI_API_KEY). Raw I/O is logged.
    Free tier for gemini-3.8-flash is 20 requests/day/model (measured 19 Oct), so not usable here."""

    URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    MIN_INTERVAL_S = 6.5   # shared by every agent in the process: ~9 requests/min, under free-tier RPM
    _last = 0.0            # class-level, so A and B share one throttle

    def __init__(self, model: str, temperature: float, log: list):
        self.model, self.temperature, self.log = model, temperature, log
        self.key = os.environ.get("GEMINI_API_KEY")
        if not self.key:
            raise RuntimeError("GEMINI_API_KEY is not set")

    def _call(self, prompt: str) -> str:
        body = {"contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": self.temperature}}
        for attempt in range(5):
            wait = GeminiAgent.MIN_INTERVAL_S - (time.time() - GeminiAgent._last)
            if wait > 0:
                time.sleep(wait)
            req = urllib.request.Request(self.URL.format(model=self.model), data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json", "x-goog-api-key": self.key})
            GeminiAgent._last = time.time()
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    out = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if e.code not in (429, 500, 503) or attempt == 4:
                    raise RuntimeError(f"Gemini HTTP {e.code}: {e.read()[:300]!r}") from None
                time.sleep(15 * (attempt + 1))
        text = "".join(p.get("text", "") for p in out["candidates"][0]["content"]["parts"])
        self.log.append({"prompt": prompt, "response": text, "model": self.model, "temperature": self.temperature})
        return text


# ---------- game ----------

@dataclass
class RoundRow:
    arm: str
    run: int
    t: int
    c_a: float
    p_a: float
    p_b: float
    msg_a: str = ""
    msg_to_b: str = ""  # M-S only: the scrambled message B actually received


def play_run(arm: Arm, agent_a: Agent, agent_b: Agent, run: int, rng, T: int = 8,
             per_run_cost: bool = False, inbox_pool: list | None = None) -> list[RoundRow]:
    """inbox_pool (M-S only): this run's B inbox for rounds 0..T-1, taken from a *different* stored M run
    (see play_arm). B reads it in place of A's own message; A's own message is still logged in msg_a."""
    hist_a, hist_b, rows = [], [], []
    run_cost = rng.choice(COSTS_A)
    for t in range(T):
        c_a = run_cost if per_run_cost else rng.choice(COSTS_A)
        obs_a = Obs("A", t, T, list(hist_a), c_a)
        if arm.channel and hasattr(agent_a, "act"):
            msg, p_a = agent_a.act(obs_a, arm)       # LLM: one call (A3)
        else:
            msg = agent_a.message(obs_a, arm) if arm.channel else None
            p_a = agent_a.price(obs_a, arm)
        inbox = msg
        if inbox_pool is not None:
            inbox = inbox_pool[t]
        obs_b = Obs("B", t, T, list(hist_b), COST_B, inbox=inbox)
        p_a = float(np.clip(p_a, P_MIN, P_MAX))
        p_b = float(np.clip(agent_b.price(obs_b, arm), P_MIN, P_MAX))
        q_a, q_b = demand(p_a, p_b)
        hist_a.append((p_a, p_b, q_a, (p_a - c_a) * q_a))
        hist_b.append((p_b, p_a, q_b, (p_b - COST_B) * q_b))
        rows.append(RoundRow(arm.name, run, t, c_a, p_a, p_b, msg or "", inbox if inbox_pool is not None else ""))
    return rows


def scramble_plan(source: dict, n_runs: int, T: int, rng) -> list[list[str]]:
    """A6: run r reads the messages of stored run s(r), with s a random derangement (s(r) != r), and
    rounds shuffled within it. A message from another run is independent of this run's c_A,t, so the
    message keeps M's form and content distribution but carries no information about A's current cost."""
    while True:
        s = rng.permutation(n_runs)
        if not np.any(s == np.arange(n_runs)):
            break
    return [[source[int(s[r])][int(i)] for i in rng.permutation(T)] for r in range(n_runs)]


def play_arm(arm: Arm, make_agents, n_runs: int, seed: int, T: int = 8, per_run_cost: bool = False,
             scramble_source: dict | None = None):
    """scramble_source (M-S only): {run: [msg_t0, ..., msg_t(T-1)]} from the stored M arm."""
    rng = np.random.default_rng(seed)
    plan = scramble_plan(scramble_source, n_runs, T, rng) if scramble_source is not None else None
    rows = []
    for r in range(n_runs):
        a, b = make_agents(rng)
        rows += play_run(arm, a, b, r, rng, T, per_run_cost, plan[r] if plan else None)
    return rows
