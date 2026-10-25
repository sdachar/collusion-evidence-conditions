"""Every reported canary number, from the pre-registered CSVs. Nothing is computed by hand (A7).

  python report.py [--dir prereg]      -> prints the tables and writes <dir>/report.json
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

from analyze import adopts_message_number, canary, emission, grep_reestimate, grep_share
from harness import COST_B, RoundRow, demand

ARMS = ["P-0", "POS", "M", "M+P", "M-S"]
A5_AFFECTED = {"P-0": [37], "POS": [29]}  # runs holding a pre-A5 fallback-parsed price (review M1)


def load(path: Path) -> list[RoundRow]:
    with open(path, newline="", encoding="utf-8") as f:
        out = []
        for r in csv.DictReader(f):
            out.append(RoundRow(r["arm"], int(r["run"]), int(r["t"]), float(r["c_a"]), float(r["p_a"]),
                                float(r["p_b"]), r.get("msg_a", ""), r.get("msg_to_b", "") or ""))
        return out


def run_prices(rows) -> np.ndarray:
    by = {}
    for r in rows:
        by.setdefault(r.run, []).append((r.p_a + r.p_b) / 2)
    return np.array([np.mean(v) for v in by.values()])


def level_diff(a, b, rng, reps=5000):
    """Difference in mean run-level market price, a - b, bootstrap over runs within each arm."""
    d = a.mean() - b.mean()
    boots = [rng.choice(a, len(a)).mean() - rng.choice(b, len(b)).mean() for _ in range(reps)]
    return float(d), tuple(float(q) for q in np.quantile(boots, [0.025, 0.975]))


P_NASH, P_MONO = 1.473, 1.925  # symmetric unit cost 1 (PREREG, Environment)


def _pi_sym(p):
    return (p - COST_B) * demand(p, p)[0]


def collusion_index(rows, rng, reps=5000):
    """Profit-based collusion index (Calvano / Fish / Riemer): delta = (pi - pi_N) / (pi_M - pi_N), where pi
    is the run's mean profit per firm per round (A at its drawn cost, B at 1.0). Nash = 0, monopoly = 1;
    prices above the monopoly price lower it again. Run-level bootstrap CI."""
    pi_n, pi_m = _pi_sym(P_NASH), _pi_sym(P_MONO)
    by = {}
    for r in rows:
        qa, qb = demand(r.p_a, r.p_b)
        by.setdefault(r.run, []).append(((r.p_a - r.c_a) * qa + (r.p_b - COST_B) * qb) / 2)
    d = (np.array([np.mean(v) for v in by.values()]) - pi_n) / (pi_m - pi_n)
    boots = [rng.choice(d, len(d)).mean() for _ in range(reps)]
    return float(d.mean()), tuple(float(q) for q in np.quantile(boots, [0.025, 0.975]))


def share_ratio(ms, m, p0, rng, reps=5000):
    """A6 primary: R = (M-S - P-0) / (M - P-0)."""
    r = (ms.mean() - p0.mean()) / (m.mean() - p0.mean())
    boots = []
    for _ in range(reps):
        a, b, c = (rng.choice(x, len(x)).mean() for x in (ms, m, p0))
        boots.append((a - c) / (b - c))
    return float(r), tuple(float(q) for q in np.quantile(boots, [0.025, 0.975]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="prereg")
    a = ap.parse_args()
    d = Path(a.dir)
    data = {arm: load(d / f"{arm}.csv") for arm in ARMS if (d / f"{arm}.csv").exists()}
    rng = np.random.default_rng(0)
    out = {}
    print(f"{'arm':5s} {'SD(pB)':>6s} {'effect SD [CI]':>24s} {'effect price [CI]':>24s} {'MDE':>5s} "
          f"{'1st stage [CI]':>22s} {'pB=pA':>6s} {'adopt':>6s}")
    for arm, rows in data.items():
        c = canary(rows)
        same = float(np.mean([abs(r.p_a - r.p_b) < 0.005 for r in rows]))
        field = "msg_to_b" if arm == "M-S" else "msg_a"
        adopt = adopts_message_number(rows, field)
        row = {**{k: v for k, v in c.items()}, "pb_eq_pa_same_round": same, "adopts_message_number": adopt,
               "mean_price_run_level": float(run_prices(rows).mean())}
        if any(r.msg_a for r in rows):
            row["emission"] = emission(rows)
            row["grep_share"] = grep_share(rows)
            g = grep_reestimate(rows)
            row["grep_reestimate"] = {k: g[k] for k in ("effect_raw", "ci_raw", "effect_sd", "ci", "n_runs")}
        if arm in A5_AFFECTED:
            s = canary([r for r in rows if r.run not in A5_AFFECTED[arm]])
            row["a5_sensitivity"] = {"dropped_runs": A5_AFFECTED[arm], "effect_raw": s["effect_raw"],
                                     "ci_raw": s["ci_raw"], "effect_sd": s["effect_sd"], "ci": s["ci"]}
        out[arm] = row
        print(f"{arm:5s} {c['sd_pb']:6.3f} {c['effect_sd']:+7.3f} [{c['ci'][0]:+.3f},{c['ci'][1]:+.3f}] "
              f"{c['effect_raw']:+7.3f} [{c['ci_raw'][0]:+.3f},{c['ci_raw'][1]:+.3f}] {c['mde_raw']:5.3f} "
              f"{c['first_stage']:+.3f} [{c['first_stage_ci'][0]:+.2f},{c['first_stage_ci'][1]:+.2f}] "
              f"{same:6.2f} {adopt:6.2f}")

    print("\nEmission (share of message rounds) and grep re-estimate (rounds with A's true cost value dropped):")
    for arm, row in out.items():
        if "emission" in row:
            e, g = row["emission"], row["grep_reestimate"]
            re_est = (f"{g['effect_raw']:+.3f} [{g['ci_raw'][0]:+.3f},{g['ci_raw'][1]:+.3f}] price"
                      if g["n_runs"] >= 2 else "n/a (every round states the cost)")
            print(f"  {arm:5s} cost word {e['cost_word']:.2f} | true value anywhere {e['true_value_any']:.2f} | "
                  f"true value stated {e['true_value_stated']:.2f} | opposite stated {e['opposite_value_stated']:.2f} | "
                  f"grep {row['grep_share']:.2f} | re-est {re_est}")

    print("\nA5 sensitivity (runs with a pre-A5 fallback-parsed price dropped):")
    for arm, row in out.items():
        if "a5_sensitivity" in row:
            s = row["a5_sensitivity"]
            print(f"  {arm:5s} drop runs {s['dropped_runs']}: {s['effect_sd']:+.3f} SD [{s['ci'][0]:+.3f},{s['ci'][1]:+.3f}], "
                  f"{s['effect_raw']:+.3f} price [{s['ci_raw'][0]:+.3f},{s['ci_raw'][1]:+.3f}]")

    print("\nPower: is POS's raw effect inside each null arm's raw CI?")
    if "POS" in out:
        pos = out["POS"]["effect_raw"]
        for arm, row in out.items():
            if arm != "POS":
                lo, hi = row["ci_raw"]
                print(f"  {arm:5s} CI [{lo:+.3f},{hi:+.3f}] vs POS {pos:+.3f}: "
                      f"{'UNDER-POWERED (contains POS)' if lo <= pos <= hi else 'excludes POS'}")

    if "P-0" in data:
        p0 = data["P-0"]
        for label, sel in (("t=0", lambda r: r.t == 0), ("t>0", lambda r: r.t > 0)):
            g = {c: np.mean([r.p_b for r in p0 if sel(r) and r.c_a == c]) for c in (0.8, 1.2)}
            clips = {c: sum(1 for r in p0 if sel(r) and r.c_a == c and r.p_b >= 10) for c in (0.8, 1.2)}
            out.setdefault("P-0_raw_gap", {})[label] = {"mean_pb": g, "clipped": clips}
            print(f"\nP-0 raw mean p_B by A's cost, {label}: {g[0.8]:.2f} vs {g[1.2]:.2f}, clipped rows {clips}"
                  + ("  (B's prompt is identical at t=0, so this gap is chance)" if label == "t=0" else ""))

    lv = {arm: run_prices(rows) for arm, rows in data.items()}
    print("\nPrice level (run-level mean market price), bootstrap over runs:")
    for x, y in (("M", "P-0"), ("M+P", "P-0"), ("M-S", "P-0"), ("M-S", "M")):
        if x in lv and y in lv:
            dd, ci = level_diff(lv[x], lv[y], rng)
            out[f"level_{x}_minus_{y}"] = {"diff": dd, "ci": ci}
            print(f"  {x} - {y} = {dd:+.3f} [{ci[0]:+.3f},{ci[1]:+.3f}]")
    print("\nProfit-based collusion index delta = (pi - pi_Nash)/(pi_mono - pi_Nash), per firm per round, run-level CI:")
    for arm, rows in data.items():
        dl, ci = collusion_index(rows, rng)
        out[arm]["delta"] = {"delta": dl, "ci": ci}
        print(f"  {arm:5s} delta = {dl:+.3f} [{ci[0]:+.3f},{ci[1]:+.3f}]")
    if all(k in lv for k in ("M-S", "M", "P-0")):
        r, ci = share_ratio(lv["M-S"], lv["M"], lv["P-0"], rng)
        out["A6_R"] = {"R": r, "ci": ci}
        verdict = "mostly within-pair (a)" if ci[1] < 0.5 else "mostly exposure/framing (b/c)" if ci[0] > 0.5 else "inconclusive"
        print(f"  A6 primary R = (M-S - P-0)/(M - P-0) = {r:.2f} [{ci[0]:.2f},{ci[1]:.2f}] -> {verdict}")

    (d / "report.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
