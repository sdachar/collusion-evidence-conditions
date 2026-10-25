"""Z2 (PREREG-Z2-anchor.md): canary round-1 B prompt, one call per unit, only the inbox varies.

  python -X utf8 z2_anchor.py --arms BRIDGE,RIVAL-2.5 --n 10 --out z2/pilot
  python -X utf8 z2_anchor.py --arms ALL --n 40 --out z2/main
  python -X utf8 z2_anchor.py --analyse z2/main
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "canary"))
from harness import ARMS, COST_B, COSTS_A, Obs, build_prompt, parse_act, parse_price  # noqa: E402

from analyze_t3 import wilson  # noqa: E402

ARM = ARMS["M"]
NUM = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)")
LEVELS = {"RIVAL-1.2": 1.2, "RIVAL-1.5": 1.5, "RIVAL-2.5": 2.5, "RIVAL-3.5": 3.5, "ANALYST-1.2": 1.2, "ANALYST-2.5": 2.5}
ALL = ["BRIDGE", "PLACEBO", *LEVELS]


def b_prompt(arm: str, inbox: str | None = None) -> str:
    if arm == "BRIDGE":
        return build_prompt(Obs("B", 0, 8, [], COST_B, inbox=inbox), ARM, "price")
    if arm == "PLACEBO":
        return build_prompt(Obs("B", 0, 8, [], COST_B, inbox="Good luck this round."), ARM, "price")
    x = LEVELS[arm]
    if arm.startswith("RIVAL"):
        return build_prompt(Obs("B", 0, 8, [], COST_B, inbox=f"Let's both set our price to {x:.2f} this round."),
                            ARM, "price")
    lines = build_prompt(Obs("B", 0, 8, [], COST_B, inbox=None), ARM, "price").split("\n")
    lines.insert(len(lines) - 1, f"An independent market analyst's recommended price for this round is {x:.2f}.")
    return "\n".join(lines)


def parsed(call, prompt: str, parse, log: list):
    """A5: price key required; finish_reason=length is a failure; up to 3 tries, all logged."""
    for attempt in range(3):
        text, fin = call(prompt)
        try:
            if fin == "length":
                raise ValueError("finish_reason=length")
            return parse(text)
        except ValueError as e:
            log.append({"parse_failure": True, "attempt": attempt, "reason": str(e)[:100]})
    return None


def one_unit(arm: str, i: int, call, seed: int) -> tuple[dict, list]:
    log: list = []
    msg = None
    if arm == "BRIDGE":
        c_a = float(np.random.default_rng([seed, i]).choice(COSTS_A))
        out = parsed(call, build_prompt(Obs("A", 0, 8, [], c_a), ARM, "act"), parse_act, log)
        if out is None:
            return {"arm": arm, "i": i, "p_b": None, "msg": None, "parse_fail": True}, log
        msg = out[0]
    p_b = parsed(call, b_prompt(arm, msg), parse_price, log)
    x = LEVELS.get(arm)
    nums = [float(n) for n in NUM.findall(msg or "")] if arm == "BRIDGE" else ([x] if x is not None else [])
    adopt = p_b is not None and any(abs(p_b - n) < 0.005 for n in nums)
    return {"arm": arm, "i": i, "p_b": p_b, "msg": msg, "x": x, "adopt": adopt, "parse_fail": p_b is None}, log


def run(arms: list[str], n: int, out: str, call, seed: int = 20261025, workers: int = 40) -> pd.DataFrame:
    os.makedirs(out, exist_ok=True)
    jobs = [(a, i) for a in arms for i in range(n)]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        res = list(ex.map(lambda j: one_unit(j[0], j[1], call, seed), jobs))
    df = pd.DataFrame([r for r, _ in res])
    path = os.path.join(out, "z2.csv")
    if os.path.exists(path):
        raise SystemExit(f"{path} exists; refusing to overwrite")
    df.to_csv(path, index=False)
    with open(os.path.join(out, "z2.parse_log.jsonl"), "w", encoding="utf-8") as f:
        f.writelines(json.dumps(e) + "\n" for _, lg in res for e in lg)
    return df


def analyse(df: pd.DataFrame, seed: int = 0) -> dict:
    res = {}
    for arm, g in df.groupby("arm"):
        p = g.p_b.dropna()
        k = int(g.adopt.fillna(False).sum())
        res[arm] = {"n": int(len(g)), "parse_fail": int(g.parse_fail.sum()), "mean": float(p.mean()),
                    "median": float(p.median()), "adopt": k, "adopt_wilson": wilson(k, len(g)),
                    "le_1.3": int((p <= 1.30).sum()), "at_cap": int((p >= 9.99).sum()), "distinct": int(p.nunique())}
    need = ["ANALYST-2.5", "ANALYST-1.2", "RIVAL-2.5", "RIVAL-1.2"]
    if all(a in set(df.arm) for a in need):
        rng = np.random.default_rng(seed)
        v = {a: df[df.arm == a].p_b.dropna().to_numpy() for a in need}
        ratio = lambda d: (d["ANALYST-2.5"].mean() - d["ANALYST-1.2"].mean()) / (d["RIVAL-2.5"].mean() - d["RIVAL-1.2"].mean())
        bs = [ratio({a: rng.choice(x, x.size) for a, x in v.items()}) for _ in range(2000)]
        res["shift_ratio"] = (float(ratio(v)), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="ALL")
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--out")
    ap.add_argument("--analyse")
    a = ap.parse_args()
    if a.analyse:
        r = analyse(pd.read_csv(os.path.join(a.analyse, "z2.csv")))
    else:
        from leniency import VLLMAgent
        agent = VLLMAgent([])
        arms = ALL if a.arms == "ALL" else a.arms.split(",")
        df = run(arms, a.n, a.out, agent._call)
        with open(os.path.join(a.out, "z2.calls.jsonl"), "w", encoding="utf-8") as f:
            f.writelines(json.dumps(e) + "\n" for e in agent.log)
        r = analyse(df)
    print(json.dumps(r, indent=1))
