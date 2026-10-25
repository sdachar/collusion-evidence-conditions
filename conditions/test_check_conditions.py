import numpy as np
import pytest

from check_conditions import (FAIL, NA, PASS, auroc, correlation_ci, label_only_baseline,
                              leave_one_statistic_out, leave_one_statistic_out_counts, placebo_fpr,
                              unit_of_analysis, wilson_ci)


def test_riemer_null_ci_reproduces_published_reread():
    # reading-list.md: r = 0.194 over n = 7 steering magnitudes -> CI roughly [-0.66, +0.83]
    lo, hi = correlation_ci(0.194, 7)
    assert lo == pytest.approx(-0.65, abs=0.02)
    assert hi == pytest.approx(0.83, abs=0.02)
    # the paper's claim is a null: it FAILs because the CI cannot rule out a strong effect
    v = unit_of_analysis(r=0.194, n=7, claim_is_null=True)
    assert v.verdict == FAIL and "null claim" in v.detail
    # the same table's positive cell r = 0.771 (p = 0.042) still clears zero, so not a blanket FAIL
    assert unit_of_analysis(r=0.771, n=7).verdict == PASS


def test_null_claim_with_tight_ci_passes():
    # review M6: the old rule FAILed exactly the ideal evidence for a null
    assert unit_of_analysis(r=0.0, n=10_000, claim_is_null=True).verdict == PASS
    assert unit_of_analysis(r=0.0, n=10_000).verdict == FAIL  # read as a positive claim, it fails


def test_count_mode_one_negative_unit_fails():
    assert unit_of_analysis(n_units=1, unit_note="1 negative configuration").verdict == FAIL
    assert unit_of_analysis(n_units=40).verdict == PASS


def test_placebo_rule_and_independence():
    s = np.r_[np.zeros(9999), [0.5]]
    assert placebo_fpr(s, 0.5, 1e-3, rule=">").value == 0.0       # the instrument's own rule
    assert placebo_fpr(s, 0.5, 1e-3, rule=">=").value == 1e-4
    assert placebo_fpr(np.zeros(100_000), 0.5, 1e-3, independent=False).verdict == NA


def test_run_spec_effect_instrument_row():
    from check_conditions import run_spec
    vs = run_spec({"label_by_design": "randomised", "single_statistic": "z", "placebo_ci": [-0.5, 0.1],
                   "n_units": 40})
    assert [v.verdict for v in vs] == [PASS, PASS, PASS, PASS]
    assert run_spec({"placebo_ci": [0.1, 0.5]})[2].verdict == FAIL


def test_auroc_basic():
    assert auroc([0.9, 0.8, 0.1, 0.2], [1, 1, 0, 0]) == 1.0
    assert auroc([0.5, 0.5], [1, 0]) == 0.5


def test_label_only_fails_when_role_defines_positive():
    roles = ["colluder"] * 20 + ["honest"] * 20
    labels = [1] * 20 + [0] * 20  # NARCBench-style: positives are the instructed role
    assert label_only_baseline(roles, labels).verdict == FAIL


def test_label_only_passes_when_role_is_uninformative():
    rng = np.random.default_rng(1)
    roles = ["a", "b"] * 50
    labels = rng.integers(0, 2, 100)
    assert label_only_baseline(roles, labels).verdict == PASS


def test_leave_one_out_catches_carrying_statistic():
    # statistic 0 fires on every positive; statistics 1, 2 almost never -> headline carried by s0
    y = np.array([1] * 50 + [0] * 50)
    X = np.zeros((100, 3))
    X[:50, 0] = 1.0
    X[:5, 1] = 1.0
    v = leave_one_statistic_out(X, [0.5, 0.5, 0.5], y, ["oracle", "mi", "perm"])
    assert v.verdict == FAIL and "oracle" in v.detail


def test_leave_one_out_counts_colludebench_ablation():
    # ablation.json at alpha 1e-2: union 15/17; without permutation_invariance 7/17
    minus = {"permutation_invariance": (7, 17), "acceptance_bias": (12, 17), "cross_run_mi": (15, 17)}
    v = leave_one_statistic_out_counts((15, 17), minus)
    assert v.verdict == FAIL and "permutation_invariance" in v.detail
    assert v.value == pytest.approx(8 / 17)
    assert leave_one_statistic_out_counts((15, 17), {"a": (15, 17), "b": (14, 17)}).verdict == PASS


def test_leave_one_out_passes_redundant_union():
    y = np.array([1] * 50 + [0] * 50)
    X = np.zeros((100, 2))
    X[:50, :] = 1.0  # either statistic alone catches everything
    assert leave_one_statistic_out(X, [0.5, 0.5], y).verdict == PASS


def test_placebo_fpr_verdicts():
    assert placebo_fpr(None, None, 1e-3).verdict == NA
    assert placebo_fpr(np.zeros(5000), 0.5, 1e-3).verdict == PASS          # 0/5000, upper ~7.7e-4
    assert placebo_fpr(np.r_[np.ones(99), np.zeros(1)], 0.5, 1e-3).verdict == FAIL  # ColludeBench-style 0.99
    assert placebo_fpr(np.zeros(50), 0.5, 1e-3).verdict == NA              # too few units to tell


def test_wilson_zero_events():
    lo, hi = wilson_ci(0, 5000)
    assert lo == 0.0 and hi < 1e-3


def test_unit_of_analysis_cluster_modes():
    assert unit_of_analysis().verdict == NA
    vals, cl = np.ones(30), np.repeat(np.arange(3), 10)
    assert unit_of_analysis(vals, cl, claimed=1.0).verdict == FAIL  # 3 clusters
    rng = np.random.default_rng(0)
    vals = rng.normal(0.5, 0.2, 400)
    cl = np.repeat(np.arange(40), 10)
    assert unit_of_analysis(vals, cl, claimed=0.5).verdict == PASS
