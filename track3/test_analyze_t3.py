import numpy as np
import pandas as pd
import pytest

from analyze_t3 import analyse, boot_diff, run_table, wilson
from leniency import P_M, P_N, REGIMES, ScriptedCartel, play_arm, rows_to_dicts


def _df(price_pre, price_post, runs=10, T=16, k=8, msg="price 1.9"):
    rows = []
    for r in range(runs):
        for t in range(T):
            p = price_pre if t < k else price_post
            rows.append(dict(arm="X", run=r, t=t, p_a=p, p_b=p, msg_a=msg, rep_a=False, rep_b=False,
                             ver_a=False, ver_b=False, audit=False, convicted=False, led_a=0.0, led_b=0.0))
    return pd.DataFrame(rows)


def test_delta_anchors_in_run_table():
    rt = run_table(_df(P_N, P_M), 8)
    assert rt.delta_pre.mean() == pytest.approx(0, abs=0.01)
    assert rt.delta_post.mean() == pytest.approx(1, abs=0.01)


def test_did_removes_common_drift():
    # both arms drift up by 0.2; the intervention arm has no extra effect -> DiD = 0
    tabs = {"R0": run_table(_df(1.8, 2.0), 8), "R2": run_table(_df(1.8, 2.0), 8)}
    est, lo, hi = analyse(tabs)["R2"]["price_did"]
    assert est == pytest.approx(0) and lo <= 0 <= hi
    tabs["R2"] = run_table(_df(1.8, 1.6), 8)               # arm falls 0.2 while control rises 0.2
    assert analyse(tabs)["R2"]["price_did"][0] == pytest.approx(-0.4)


def test_boot_ci_covers_truth():
    rng = np.random.default_rng(0)
    x, y = rng.normal(1.0, 1, 200), rng.normal(0.0, 1, 200)
    est, lo, hi = boot_diff(x, y)
    assert lo < 1.0 < hi and hi - lo < 0.6


def test_wilson_zero():
    lo, hi = wilson(0, 40)
    assert lo == 0 and 0.08 < hi < 0.1


def test_ladder_table_primary_and_snitch_and_stay():
    from analyze_t3 import ladder_table
    from leniency import ScriptedProposer
    from test_leniency import QuotingB
    rg = REGIMES["R3-50"]
    df = pd.DataFrame(rows_to_dicts(play_arm(rg, lambda rng: (ScriptedProposer(rng), QuotingB(8)), 10, seed=3)))
    lt = ladder_table(df, 8)
    assert lt.first_attempt.all() and lt.verified.all()               # reports at round index 8, true quote
    assert lt.snitch_stay.all()                                        # keeps pricing 1.90 after reporting
    assert (lt.follow_pre == 1).all()
    df2 = pd.DataFrame(rows_to_dicts(play_arm(rg, lambda rng: (ScriptedProposer(rng), QuotingB(99)), 10, seed=3)))
    assert not ladder_table(df2, 8).any_attempt.any()


def test_end_to_end_on_scripted_arms():
    tabs = {arm: run_table(pd.DataFrame(rows_to_dicts(
        play_arm(REGIMES[arm], lambda rng: (ScriptedCartel(rng, 9), ScriptedCartel(rng)), 12, seed=1))), 8)
        for arm in ("R0", "R2", "PL")}
    res = analyse(tabs)
    assert res["R0"]["reported"]["k"] == 0
    assert res["PL"]["verified"]["k"] == 0 and res["PL"]["reported"]["k"] == 12
    assert res["R2"]["verified"]["k"] + res["R2"]["audited"]["k"] == 12   # every run convicted one way
