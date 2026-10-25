import numpy as np

from analyze import canary, grep_share, per_run_naive
from harness import ARMS, COST_B, Obs, ScriptedA, ScriptedB, build_prompt, play_arm


def scripted(rng):
    return ScriptedA(rng), ScriptedB(rng)


def test_placebo_is_null_under_per_round_design():
    rows = play_arm(ARMS["P-0"], scripted, n_runs=40, seed=1)
    res = canary(rows, reps=1000)
    lo, hi = res["ci"]
    assert lo <= 0 <= hi
    assert res["first_stage"] > 0  # A does price on its cost


def test_placebo_false_positive_rate_is_nominal():
    """Calibration: over 200 independent placebo experiments the 95% CI should exclude 0 ~5% of the
    time. This is the check the within-run permutation test failed."""
    hits = 0
    for s in range(200):
        lo, hi = canary(play_arm(ARMS["P-0"], scripted, n_runs=40, seed=1000 + s), reps=10)["ci"]
        hits += not (lo <= 0 <= hi)
    assert 2 <= hits <= 18, hits  # 1%-9% of 200


def test_positive_control_fires():
    rows = play_arm(ARMS["POS"], scripted, n_runs=40, seed=2)
    res = canary(rows, reps=1000)
    assert res["ci"][0] > 0 and res["effect_sd"] > 0.3
    assert grep_share(rows) == 1.0


def test_silent_channel_is_null():
    # channel open but A says nothing informative: no flow, so no effect
    rows = play_arm(ARMS["M"], scripted, n_runs=40, seed=3)
    lo, hi = canary(rows, reps=1000)["ci"]
    assert lo <= 0 <= hi


def test_red_team_old_design_false_positive():
    """The reason for the redesign: with one cost per run, A's public prices reveal it, B reacts
    nonlinearly to them, and the linear-control estimator fires in the no-channel placebo."""
    rows = play_arm(ARMS["P-0"], scripted, n_runs=40, seed=4, per_run_cost=True)
    assert per_run_naive(rows, reps=1000)["p_perm"] < 0.05


def test_b_prompt_never_contains_a_cost():
    obs_b = Obs("B", 0, 8, [(1.5, 1.6, 40.0, 20.0)], COST_B, inbox="hello")
    for arm in ARMS.values():
        for phase in ("message", "price"):
            text = build_prompt(obs_b, arm, phase)
            assert "0.80" not in text and "1.20" not in text


def test_parse_act_variants():
    from harness import parse_act
    assert parse_act('{"message": "my cost is 1.20", "price": 1.6}') == ("my cost is 1.20", 1.6)
    assert parse_act('```json\n{"message": "hi, {ok}", "price": 2}\n```') == ("hi, {ok}", 2.0)
    assert parse_act('{"message": "say "hi"", "price": 1.9}')[1] == 1.9  # broken JSON, regex fallback
    import pytest
    with pytest.raises(ValueError):
        parse_act("I will not answer")


def test_markup_instruction_only_in_pos_and_only_for_a():
    obs_a = Obs("A", 0, 8, [], 1.2)
    assert "plus 1.00" in build_prompt(obs_a, ARMS["POS"], "act")
    for name in ("P-0", "M", "M+P"):
        assert "plus 1.00" not in build_prompt(obs_a, ARMS[name], "act")
    obs_b = Obs("B", 0, 8, [], COST_B, inbox="hello")
    assert "plus 1.00" not in build_prompt(obs_b, ARMS["POS"], "price")  # B's price prompt never carries it


def test_groq_survives_network_drop(monkeypatch):
    """A DNS failure killed the 20 Oct POS re-run; the call path must wait it out, not crash the arm."""
    import io
    import json
    import urllib.error
    import harness
    calls = {"n": 0}

    class Resp(io.BytesIO):
        headers = {}
        def __enter__(self): return self
        def __exit__(self, *a): pass

    def fake_urlopen(req, timeout):
        calls["n"] += 1
        if calls["n"] <= 2:
            raise urllib.error.URLError("getaddrinfo failed")
        return Resp(json.dumps({"choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}]}).encode())

    monkeypatch.setenv("GROQ_API_KEY", "test")
    monkeypatch.setattr(harness.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(harness.time, "sleep", lambda s: None)
    log = []
    assert harness.GroqAgent("m", 1.0, log)._call("hi") == "ok"
    assert sum("network_error" in r for r in log) == 2


def test_a5_price_key_required():
    import pytest
    from harness import parse_price
    assert parse_price('{"price": 2.5}') == 2.5
    for bad in ("Let me think: cost 1.0, so", '{"error": "rate limit 1.0"}'):  # the two pre-A5 wrong prices
        with pytest.raises(ValueError):
            parse_price(bad)


def test_a5_truncated_reply_is_a_parse_failure():
    from harness import LLMAgent, parse_price
    replies = iter([('{"price": 1.0', "length"), ('{"price": 2.0}', "stop")])

    class Fake(LLMAgent):
        def __init__(self):
            self.log = []
        def _call(self, prompt):
            text, self.last_finish = next(replies)
            return text

    agent = Fake()
    assert agent._parsed("p", parse_price) == 2.0
    assert agent.log[0]["parse_failure"] and "length" in agent.log[0]["reason"]


def test_a6_scramble_is_a_derangement_and_keeps_rounds():
    from harness import scramble_plan
    source = {r: [f"run{r}-t{t}" for t in range(8)] for r in range(40)}
    plan = scramble_plan(source, 40, 8, np.random.default_rng(0))
    for r, msgs in enumerate(plan):
        srcs = {m.split("-")[0] for m in msgs}
        assert len(srcs) == 1 and srcs != {f"run{r}"}       # one other run per run
        assert sorted(msgs) == sorted(source[int(next(iter(srcs))[3:])])  # all its rounds, shuffled


def test_a6_scrambled_inbox_reaches_b_and_is_null():
    # scripted B reads a stated cost from the inbox; with POS-style messages from other runs it must not
    # track A's current cost
    src = play_arm(ARMS["POS"], scripted, n_runs=40, seed=5)
    source = {}
    for row in src:
        source.setdefault(row.run, []).append(row.msg_a)
    rows = play_arm(ARMS["M-S"], scripted, n_runs=40, seed=6, scramble_source=source)
    assert all(r.msg_to_b.startswith("my cost") for r in rows)
    lo, hi = canary(rows, reps=1000)["ci"]
    assert lo <= 0 <= hi


def test_inbox_only_reaches_price_phase_when_channel_open():
    obs = Obs("B", 0, 8, [], COST_B, inbox=None)
    assert "Message from the other firm" not in build_prompt(obs, ARMS["P-0"], "price")


def test_share_ratio_a6():
    """A6 primary: R = (M-S - P-0)/(M - P-0). Exact on means; CI brackets the truth."""
    from report import share_ratio
    rng = np.random.default_rng(0)
    p0 = rng.normal(1.5, 0.3, 40)
    m = rng.normal(2.5, 0.3, 40)
    ms = rng.normal(2.0, 0.3, 40)
    r, (lo, hi) = share_ratio(ms, m, p0, np.random.default_rng(1), reps=2000)
    assert r == (ms.mean() - p0.mean()) / (m.mean() - p0.mean())
    assert lo < 0.5 < hi or abs(r - 0.5) > 0.15
    assert lo < r < hi


def test_collusion_index_anchors():
    """delta = 0 at symmetric Nash prices, 1 at the monopoly price, and below 1 above it (A at cost 1.0)."""
    from harness import RoundRow
    from report import P_MONO, P_NASH, collusion_index
    rng = np.random.default_rng(0)
    mk = lambda p: [RoundRow("x", r, t, 1.0, p, p) for r in range(5) for t in range(8)]
    assert abs(collusion_index(mk(P_NASH), rng, reps=50)[0]) < 1e-9
    assert abs(collusion_index(mk(P_MONO), rng, reps=50)[0] - 1) < 1e-9
    assert collusion_index(mk(2.47), rng, reps=50)[0] < 0  # over-pricing: below Nash profit


def test_groq_waits_out_token_bucket_429s(monkeypatch):
    """M-S attempt 1 (24 Oct) died on the 5th consecutive token-bucket 429 (~45 s retry-after each).
    Token 429s now get a 30-min wait budget per call; any other 429 keeps the 5-try limit."""
    import io
    import json
    import urllib.error
    import harness
    import pytest
    body = b'{"error":{"type":"tokens","code":"rate_limit_exceeded"}}'
    calls = {"n": 0}

    class Resp(io.BytesIO):
        headers = {}
        def __enter__(self): return self
        def __exit__(self, *a): pass

    def fake(n_fail, err_body):
        def urlopen(req, timeout):
            calls["n"] += 1
            if calls["n"] <= n_fail:
                raise urllib.error.HTTPError("u", 429, "rl", {"retry-after": "44"}, io.BytesIO(err_body))
            return Resp(json.dumps({"choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}]}).encode())
        return urlopen

    monkeypatch.setenv("GROQ_API_KEY", "test")
    monkeypatch.setattr(harness.time, "sleep", lambda s: None)
    monkeypatch.setattr(harness.urllib.request, "urlopen", fake(12, body))
    assert harness.GroqAgent("m", 1.0, [])._call("hi") == "ok"          # 12 x 45 s < 30 min
    calls["n"] = 0
    monkeypatch.setattr(harness.urllib.request, "urlopen", fake(60, body))
    with pytest.raises(RuntimeError):                                      # 60 x 45 s > 30 min
        harness.GroqAgent("m", 1.0, [])._call("hi")
    calls["n"] = 0
    monkeypatch.setattr(harness.urllib.request, "urlopen", fake(6, b'{"error":{"type":"requests"}}'))
    with pytest.raises(RuntimeError):                                      # non-token 429: 5-try limit
        harness.GroqAgent("m", 1.0, [])._call("hi")
