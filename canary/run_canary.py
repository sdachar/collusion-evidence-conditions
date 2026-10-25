"""Run canary arms. `--agents scripted` is free and offline; `--agents gemini` needs GEMINI_API_KEY.

Writes out/<arm>.csv (one row per round) and out/<arm>.calls.jsonl (every raw prompt and reply).
An arm that crashes writes out/<arm>.FAILED and no CSV: a crash must never look like a result.

  python run_canary.py --agents scripted --arms P-0 M POS
  python run_canary.py --agents gemini --model gemini-2.5-flash --runs 10 --arms POS   # Tue gate smoke test
"""
from __future__ import annotations

import argparse
import csv
import json
import traceback
from dataclasses import asdict
from pathlib import Path

from analyze import canary, grep_share
from harness import ARMS, GeminiAgent, GroqAgent, ScriptedA, ScriptedB, play_arm


def wait_for_quota(model: str, need: int, refill_s: float = 86.4):
    """Poll Groq's x-ratelimit-remaining-requests (one 5-token request per check) until >= need."""
    import time
    import urllib.error
    import urllib.request
    key = GroqAgent(model, 1.0, []).key
    body = json.dumps({"model": model, "max_tokens": 5, "messages": [{"role": "user", "content": "Reply OK"}]}).encode()
    while True:
        req = urllib.request.Request(GroqAgent.URL, data=body, headers={
            "Content-Type": "application/json", "Authorization": f"Bearer {key}", "User-Agent": "canary-harness/0.1"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                left = int(r.headers.get("x-ratelimit-remaining-requests", 0))
        except (urllib.error.URLError, OSError) as e:  # a DNS failure here killed the 20 Oct POS re-run
            print(f"{time.strftime('%H:%M')} poll failed ({e!r}), retrying in 5 min", flush=True)
            time.sleep(300)
            continue
        print(f"{time.strftime('%H:%M')} quota {left} / need {need}", flush=True)
        if left >= need:
            return
        time.sleep(min(3600, (need - left) * refill_s + 60))


def load_messages(path: str, T: int) -> dict:
    """{run: [msg_a at t=0..T-1]} from a stored arm CSV; refuses an incomplete run."""
    out: dict = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.setdefault(int(r["run"]), {})[int(r["t"])] = r["msg_a"]
    for run, msgs in out.items():
        if sorted(msgs) != list(range(T)):
            raise ValueError(f"{path}: run {run} has rounds {sorted(msgs)}, need 0..{T - 1}")
    return {run: [msgs[t] for t in range(T)] for run, msgs in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agents", choices=["scripted", "gemini", "groq"], required=True)
    ap.add_argument("--arms", nargs="+", default=["P-0", "M", "M+P", "POS"])
    ap.add_argument("--runs", type=int, default=40)
    ap.add_argument("--rounds", type=int, default=8)
    # gemini-2.5-flash returns 404 for new users (19 Oct 2026); Gemini 3+ guidance is temperature 1.0
    ap.add_argument("--model", default=None, help="default: qwen/qwen3.8-27b (groq), gemini-3.8-flash (gemini)")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=20261019)
    ap.add_argument("--out", default="out")
    ap.add_argument("--scramble-from", default="prereg/M.csv",
                    help="M-S (A6): the stored M arm whose messages B receives, deranged across runs")
    ap.add_argument("--min-quota", type=int, default=0,
                    help="groq: sleep until this many requests remain in the daily bucket before starting")
    a = ap.parse_args()
    a.model = a.model or {"groq": "qwen/qwen3.8-27b", "gemini": "gemini-3.8-flash"}.get(a.agents)
    if a.agents == "groq" and a.min_quota:
        wait_for_quota(a.model, a.min_quota)
    out = Path(a.out)
    out.mkdir(exist_ok=True)

    for i, name in enumerate(a.arms):
        log: list = []
        if a.agents == "scripted":
            make = lambda rng: (ScriptedA(rng), ScriptedB(rng))
        else:
            cls = GeminiAgent if a.agents == "gemini" else GroqAgent
            make = lambda rng: (cls(a.model, a.temperature, log), cls(a.model, a.temperature, log))
        source = load_messages(a.scramble_from, a.rounds) if name == "M-S" else None
        try:
            rows = play_arm(ARMS[name], make, a.runs, a.seed + i, a.rounds, scramble_source=source)
        except Exception:
            (out / f"{name}.FAILED").write_text(traceback.format_exc(), encoding="utf-8")
            print(f"{name}: FAILED, see {out / (name + '.FAILED')}")
            continue
        finally:
            with open(out / f"{name}.calls.jsonl", "w", encoding="utf-8") as f:
                for rec in log:
                    f.write(json.dumps(rec) + "\n")
        with open(out / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(asdict(rows[0])))
            w.writeheader()
            w.writerows(asdict(r) for r in rows)
        res = canary(rows)
        print(f"{name}: effect {res['effect_sd']:+.3f} SD, 95% CI [{res['ci'][0]:+.3f}, {res['ci'][1]:+.3f}], "
              f"first stage {res['first_stage']:+.3f}, grep share {grep_share(rows):.2f}, runs {res['n_runs']}")


if __name__ == "__main__":
    main()
