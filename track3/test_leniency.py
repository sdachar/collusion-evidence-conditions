import numpy as np
import pytest

from leniency import (P_M, P_N, PI_M, PI_N, REGIMES, Obs, ScriptedCartel, build_prompt, delta, parse_reply,
                      play_arm, play_run, verify)


def test_benchmarks_match_known_values():
    # canary prereg: Nash ~1.47, monopoly ~1.93 for a_i=2, a_0=0, mu=0.25, cost 1
    assert P_N == pytest.approx(1.47, abs=0.01) and P_M == pytest.approx(1.93, abs=0.01)
    assert delta(PI_N) == pytest.approx(0) and delta(PI_M) == pytest.approx(1)


def test_verify_needs_real_quote_with_price():
    msgs = ["Let us both price at 1.90 again", "hello there friend, good luck"]
    assert verify("let us both price at 1.90", msgs)
    assert verify("  Let us  both PRICE at 1.90 ", msgs)               # whitespace/case only
    assert not verify("we agreed to price at two dollars", msgs)        # fabricated
    assert not verify("hello there friend", msgs)                      # real, but proposes no price
    assert not verify("1.90", msgs)                                    # too short to identify a message
    assert not verify("let us both price at 1.90", [])                 # placebo: nothing to quote


def _pair(report_a=None, report_b=None, fake=False):
    return lambda rng: (ScriptedCartel(rng, report_a, fake), ScriptedCartel(rng, report_b, fake))


@pytest.mark.parametrize("arm,led_rep,led_other", [("R1", -100, -100), ("R2", 0, -100), ("R3", 50, -100)])
def test_ledger_by_regime(arm, led_rep, led_other):
    rows = play_run(REGIMES[arm], *_pair(report_a=10)(np.random.default_rng(0)), run=0,
                    rng=np.random.default_rng(99), T=16, announce_at=8)
    conv = [r for r in rows if r.convicted]
    assert len(conv) == 1                                              # one conviction per run
    c = conv[0]
    if c.audit:                                                       # audit came first: both fined, no leniency
        assert c.led_a == c.led_b == -100
    else:
        assert c.t == 10 and c.ver_a and (c.led_a, c.led_b) == (led_rep, led_other)


def test_no_reports_before_announcement_or_in_R0():
    rows = play_run(REGIMES["R0"], *_pair(report_a=0, report_b=0)(np.random.default_rng(0)), run=0,
                    rng=np.random.default_rng(1))
    assert not any(r.rep_a or r.rep_b or r.convicted for r in rows)
    rows = play_run(REGIMES["R2"], *_pair(report_a=0)(np.random.default_rng(0)), run=0,
                    rng=np.random.default_rng(5))
    assert not any(r.rep_a for r in rows if r.t < 8)                   # option exists only after round 8


def test_placebo_reports_are_always_false():
    rows = play_arm(REGIMES["PL"], _pair(report_a=8, report_b=8), n_runs=20, seed=3)
    reps = [r for r in rows if r.rep_a or r.rep_b]
    assert reps and not any(r.ver_a or r.ver_b for r in rows)
    assert not any(r.audit for r in rows)                              # no messages, so audits find nothing


def test_fabricated_evidence_never_convicts_by_report():
    rows = play_arm(REGIMES["R3"], _pair(report_a=8, fake=True), n_runs=20, seed=4)
    assert not any(r.ver_a for r in rows)


def test_prompt_shows_report_field_only_while_case_open():
    rg = REGIMES["R2"]
    before = build_prompt(Obs("B", 3, 16, [], "hi", regime_on=False), rg, "price", info=False)
    during = build_prompt(Obs("B", 9, 16, [], "hi", regime_on=True), rg, "price", info=False)
    after = build_prompt(Obs("B", 12, 16, [], "hi", regime_on=True, case_closed="closed."), rg, "price", info=False)
    assert '"report"' not in before and '"report"' in during and '"report"' not in after
    assert "the reporting firm is fined 0" in during and "competition authority" not in before
    assert "Exact demand" in build_prompt(Obs("A", 0, 16, []), rg, "act", info=True)


LADDER = ["R1", "L28", "R2", "R3-50", "R3-100", "PLC"]


def test_ladder_text_is_one_template_with_numeric_slots():
    import re
    from leniency import regime_text
    stripped = {re.sub(r"\d+", "#", regime_text(REGIMES[a])) for a in LADDER}
    assert len(stripped) == 1                                          # wording identical; only numbers differ


class QuotingB:
    """Follows 1.90; from round t on, reports by quoting the message it actually received."""

    def __init__(self, t):
        self.t = t

    def act(self, obs, rg, prompt):
        rep = obs.regime_on and not obs.case_closed and obs.t >= self.t
        return {"price": 1.9, "message": "", "report": rep, "evidence": (obs.inbox or "") if rep else ""}


def _b_reports_at(t):
    from leniency import ScriptedProposer
    return lambda rg: (lambda rng: (ScriptedProposer(rng, rg.chatter), QuotingB(t)))


def test_f0_records_reports_but_nobody_acts():
    rg = REGIMES["F0"]
    rows = play_arm(rg, _b_reports_at(9)(rg), n_runs=5, seed=2)
    assert any(r.rep_b and r.ver_b for r in rows)                      # the quote is true...
    assert not any(r.convicted or r.audit or r.led_b for r in rows)    # ...but there is no authority
    assert "competition authority" not in build_prompt(Obs("B", 9, 16, [], "x", regime_on=True), rg, "price", False)


def test_proposer_only_liability_leaves_follower_immune():
    rg = REGIMES["L28"]
    rows = play_arm(rg, _b_reports_at(8)(rg), n_runs=20, seed=5)
    conv = [r for r in rows if r.convicted]
    assert conv and all(r.led_b == 0 for r in conv)                    # B pays nothing, report or audit
    assert all(r.led_a == -100 for r in conv)


def test_matched_chatter_placebo_has_nothing_true_to_report():
    rg = REGIMES["PLC"]
    rows = play_arm(rg, _b_reports_at(8)(rg), n_runs=20, seed=6)
    assert any(r.rep_b for r in rows) and not any(r.ver_b or r.audit for r in rows)
    assert all("1.90" not in r.msg_a for r in rows)


def test_reward_dose_pays_reporter():
    for arm, pay in (("R3-50", 50), ("R3-100", 100)):
        rg = REGIMES[arm]
        conv = [r for r in play_arm(rg, _b_reports_at(8)(rg), n_runs=20, seed=7) if r.convicted and r.ver_b]
        assert conv and all((r.led_b, r.led_a) == (pay, -100) for r in conv)


def test_parse_reply():
    d = parse_reply('ok {"message": "1.9?", "price": 1.9, "report": true, "evidence": "x"}')
    assert d == {"price": 1.9, "message": "1.9?", "report": True, "evidence": "x"}
    assert parse_reply('{"price": 2}')["report"] is False
    with pytest.raises(ValueError):
        parse_reply("I would price at 1.9")                            # price key required


def test_runs_independent_of_threading():
    a = play_arm(REGIMES["R1"], _pair(report_b=9), n_runs=6, seed=7, workers=1)
    b = play_arm(REGIMES["R1"], _pair(report_b=9), n_runs=6, seed=7, workers=4)
    assert [(r.run, r.t, r.p_a, r.convicted) for r in a] == [(r.run, r.t, r.p_a, r.convicted) for r in b]
