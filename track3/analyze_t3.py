"""Run-level analysis for intervention-at-round-k designs on the track-3 harness.

Unit of analysis = the run (rounds within a run are a cluster). Every interval is a bootstrap over runs,
resampled independently within each arm. The main contrast is a difference-in-differences against R0:
(post - pre in arm) - (post - pre in R0), which removes drift that happens with no intervention.

  python analyze_t3.py <dir> [--announce 8] [--control R0]
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os

import numpy as np
import pandas as pd

from leniency import COST, PRICE_PROPOSAL, delta, demand


def run_table(df: pd.DataFrame, announce: int) -> pd.DataFrame:
    q = np.array([demand(a, b) for a, b in zip(df.p_a, df.p_b)])
    df = df.assign(price=(df.p_a + df.p_b) / 2,
                   pi=((df.p_a - COST) * q[:, 0] + (df.p_b - COST) * q[:, 1]) / 2,
                   proposal=df.msg_a.fillna("").map(lambda m: bool(PRICE_PROPOSAL.search(str(m)))),
                   post=df.t >= announce)
    g = df.groupby(["run", "post"])
    wide = g[["price", "pi", "proposal"]].mean().unstack("post")
    out = pd.DataFrame({
        "price_pre": wide[("price", False)], "price_post": wide[("price", True)],
        "delta_pre": wide[("pi", False)].map(delta), "delta_post": wide[("pi", True)].map(delta),
        "prop_pre": wide[("proposal", False)], "prop_post": wide[("proposal", True)]})
    post = df[df.post].groupby("run")
    out["reported"] = post[["rep_a", "rep_b"]].any().any(axis=1)
    out["verified"] = post[["ver_a", "ver_b"]].any().any(axis=1)
    out["audited"] = post.audit.any()
    first = df[df.post & (df.rep_a | df.rep_b)].groupby("run").t.min()
    out["first_report_t"] = first.reindex(out.index)
    return out


def ladder_table(df: pd.DataFrame, announce: int, cartel_price: float = 1.90) -> pd.DataFrame:
    """Per run, firm B only (A is scripted). PREREG-T3-leniency.md:
    - first_attempt: B tried to report in round `announce` (the first announced round; never censored,
      because reports are judged before that round's audit). PRIMARY.
    - any_attempt / attempts_per_open: over rounds in which the case was still open. SECONDARY.
    - snitch_stay: B reported, then priced within 0.05 of the cartel price in the next round.
    - follow_pre: share of pre-announcement rounds with B within 0.05 of the cartel price (pilot gate)."""
    out = []
    for run, g in df.sort_values("t").groupby("run"):
        pre, post = g[g.t < announce], g[g.t >= announce]
        conv_t = post.loc[post.convicted, "t"].min() if post.convicted.any() else None
        open_ = post[post.t <= conv_t] if conv_t is not None else post
        rep = open_[open_.rep_b]
        nxt = [g.loc[g.t == t + 1, "p_b"] for t in rep.t]
        out.append({
            "run": run,
            "first_attempt": bool(post[post.t == announce].rep_b.any()),
            "any_attempt": bool(len(rep)),
            "attempts_per_open": len(rep) / max(1, len(open_)),
            "verified": bool(open_.ver_b.any()),
            "first_t": int(rep.t.min()) if len(rep) else None,
            "snitch_stay": bool(any(len(s) and abs(float(s.iloc[0]) - cartel_price) <= 0.05 for s in nxt)),
            "follow_pre": float((abs(pre.p_b - cartel_price) <= 0.05).mean()),
            "follow_post": float((abs(post.p_b - cartel_price) <= 0.05).mean()),
            "price_post": float(post.p_b.mean()),
        })
    return pd.DataFrame(out).set_index("run")


def boot_diff(x, y=None, n: int = 2000, seed: int = 0) -> tuple[float, float, float]:
    """Mean of x (or mean(x) - mean(y)) with a 95% percentile CI, resampling runs within each arm."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    est = x.mean() - (np.asarray(y, float).mean() if y is not None else 0.0)
    bs = np.empty(n)
    for i in range(n):
        bs[i] = rng.choice(x, x.size).mean()
        if y is not None:
            y_ = np.asarray(y, float)
            bs[i] -= rng.choice(y_, y_.size).mean()
    return float(est), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, c - h), min(1.0, c + h)


def analyse(tables: dict[str, pd.DataFrame], control: str = "R0") -> dict:
    res = {}
    ctl = tables.get(control)
    for arm, rt in tables.items():
        r = {"n_runs": int(len(rt))}
        for m in ("price", "delta", "prop"):
            r[f"{m}_pre"] = boot_diff(rt[f"{m}_pre"])
            r[f"{m}_post"] = boot_diff(rt[f"{m}_post"])
            change = rt[f"{m}_post"] - rt[f"{m}_pre"]
            if ctl is not None and arm != control:
                r[f"{m}_did"] = boot_diff(change, ctl[f"{m}_post"] - ctl[f"{m}_pre"])
        for k in ("reported", "verified", "audited"):
            n_k = int(rt[k].sum())
            r[k] = {"k": n_k, "share": n_k / len(rt), "wilson": wilson(n_k, len(rt))}
        res[arm] = r
    return res


LADDER_ORDER = ["R1", "L28", "R2", "R3-50", "R3-100"]   # increasing payoff to a reporting follower


def ladder_report(d: str, announce: int = 8) -> dict:
    tabs = {}
    for f in sorted(glob.glob(os.path.join(d, "*.csv"))):
        arm = os.path.basename(f)[:-4]
        if not os.path.exists(os.path.join(d, f"{arm}.FAILED")):
            tabs[arm] = ladder_table(pd.read_csv(f, keep_default_na=False, na_values=[""]), announce)
    res = {}
    for arm, lt in tabs.items():
        n = len(lt)
        r = {"n": n}
        for k in ("first_attempt", "any_attempt", "verified", "snitch_stay"):
            kk = int(lt[k].sum())
            r[k] = (kk, wilson(kk, n))
        for k in ("follow_pre", "follow_post", "price_post", "attempts_per_open"):
            r[k] = boot_diff(lt[k])
        res[arm] = r
    if {"R1", "R3-50"} <= tabs.keys():                          # pre-registered headline contrast
        res["H1_R3-50_minus_R1_first"] = boot_diff(tabs["R3-50"].first_attempt, tabs["R1"].first_attempt)
        res["H1_R3-50_minus_R1_any"] = boot_diff(tabs["R3-50"].any_attempt, tabs["R1"].any_attempt)
    rungs = [a for a in LADDER_ORDER if a in tabs]
    if len(rungs) >= 3:
        rates = [tabs[a].first_attempt.mean() for a in rungs]
        res["ladder_rates_first"] = dict(zip(rungs, map(float, rates)))
        res["ladder_spearman"] = float(pd.Series(rates).rank().corr(pd.Series(range(len(rates))), method="pearson"))
    return res


def load(d: str, announce: int) -> dict[str, pd.DataFrame]:
    out = {}
    for f in sorted(glob.glob(os.path.join(d, "*.csv"))):
        arm = os.path.basename(f)[:-4]
        if os.path.exists(os.path.join(d, f"{arm}.FAILED")):
            continue                                   # a crash never counts as a result
        out[arm] = run_table(pd.read_csv(f), announce)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--announce", type=int, default=8)
    ap.add_argument("--control", default="R0")
    ap.add_argument("--ladder", action="store_true", help="incentive-ladder report (firm B, scripted A)")
    a = ap.parse_args()
    if a.ladder:
        r = ladder_report(a.dir, a.announce)
        with open(os.path.join(a.dir, "ladder_analysis.json"), "w", encoding="utf-8") as f:
            json.dump(r, f, indent=1, default=str)
        print(json.dumps(r, indent=1, default=str))
        raise SystemExit
    res = analyse(load(a.dir, a.announce), a.control)
    fmt = lambda t: f"{t[0]:+.3f} [{t[1]:+.3f}, {t[2]:+.3f}]"
    for arm, r in res.items():
        line = [f"{arm:3} n={r['n_runs']:2}", f"price post {fmt(r['price_post'])}", f"delta post {fmt(r['delta_post'])}"]
        if "price_did" in r:
            line += [f"DiD price {fmt(r['price_did'])}", f"DiD proposals {fmt(r['prop_did'])}"]
        line += [f"reported {r['reported']['k']}", f"verified {r['verified']['k']}", f"audited {r['audited']['k']}"]
        print(" | ".join(line))
    with open(os.path.join(a.dir, "analysis.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
