"""Run leniency arms and write one CSV + raw call log per arm. A crash writes <arm>.FAILED and no CSV,
so a failure can never look like a result (canary / _lib.sh rule).

  python run_t3.py --agents scripted --arms R0,R2 --runs 10 --out smoke
  python run_t3.py --agents vllm --arms R0 --runs 10 --T 16 --info --out pilot0 --seed 1
"""
import argparse
import json
import os
import traceback

import numpy as np
import pandas as pd

from leniency import (COST, PRICE_PROPOSAL, REGIMES, ScriptedCartel, ScriptedProposer, VLLMAgent, delta, demand,
                      play_arm, rows_to_dicts)


def summarise(df: pd.DataFrame, announce_at: int) -> dict:
    q = np.array([demand(a, b) for a, b in zip(df.p_a, df.p_b)])
    df = df.assign(pi=((df.p_a - COST) * q[:, 0] + (df.p_b - COST) * q[:, 1]) / 2,
                   proposal=df.msg_a.fillna("").map(lambda m: bool(PRICE_PROPOSAL.search(m))))
    out = {}
    for name, part in (("pre", df[df.t < announce_at]), ("post", df[df.t >= announce_at])):
        runs = part.groupby("run")
        out[name] = {"price": round(float(runs[["p_a", "p_b"]].mean().mean(axis=1).mean()), 3),
                     "delta": round(float(delta(runs.pi.mean().mean())), 3),
                     "proposal_share": round(float(part.proposal.mean()), 3)}
    post = df[df.t >= announce_at]
    out["runs_reported"] = int(post.groupby("run")[["rep_a", "rep_b"]].any().any(axis=1).sum())
    out["runs_verified"] = int(post.groupby("run")[["ver_a", "ver_b"]].any().any(axis=1).sum())
    out["runs_audited"] = int(post.groupby("run").audit.any().sum())
    out["n_runs"] = int(df.run.nunique())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agents", choices=["scripted", "vllm", "ladder", "ladder-scripted"], required=True,
                    help="vllm: both firms LLM; ladder: scripted proposer A + LLM B; *-scripted: no API calls")
    ap.add_argument("--arms", required=True)
    ap.add_argument("--runs", type=int, default=40)
    ap.add_argument("--T", type=int, default=16)
    ap.add_argument("--announce", type=int, default=8)
    ap.add_argument("--info", action="store_true", help="give agents the exact demand formula")
    ap.add_argument("--seed", type=int, default=20261024)
    ap.add_argument("--workers", type=int, default=40)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for arm in a.arms.split(","):
        csv = os.path.join(a.out, f"{arm}.csv")
        if os.path.exists(csv):
            raise SystemExit(f"{csv} exists; refusing to overwrite")
        logs: list = []
        rg = REGIMES[arm]
        if a.agents == "scripted":
            make = lambda rng: (ScriptedCartel(rng, 10), ScriptedCartel(rng))
        elif a.agents == "ladder-scripted":
            make = lambda rng, rg=rg: (ScriptedProposer(rng, rg.chatter), ScriptedCartel(rng, 10))
        elif a.agents == "ladder":
            make = lambda rng, rg=rg: (ScriptedProposer(rng, rg.chatter), VLLMAgent(logs))
        else:
            make = lambda rng: (VLLMAgent(logs), VLLMAgent(logs))
        try:
            rows = play_arm(REGIMES[arm], make, a.runs, a.seed + list(REGIMES).index(arm), a.T, a.announce,
                            a.info, a.workers)
        except Exception:
            with open(os.path.join(a.out, f"{arm}.FAILED"), "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())
            with open(os.path.join(a.out, f"{arm}.calls.jsonl"), "w", encoding="utf-8") as f:
                f.writelines(json.dumps(e) + "\n" for e in logs)
            raise
        df = pd.DataFrame(rows_to_dicts(rows))
        df.to_csv(csv, index=False)
        with open(os.path.join(a.out, f"{arm}.calls.jsonl"), "w", encoding="utf-8") as f:
            f.writelines(json.dumps(e) + "\n" for e in logs)
        s = summarise(df, a.announce)
        s.update(arm=arm, T=a.T, info=a.info, seed=a.seed, parse_failures=sum(1 for e in logs if e.get("parse_failure")))
        with open(os.path.join(a.out, f"{arm}.summary.json"), "w", encoding="utf-8") as f:
            json.dump(s, f, indent=1)
        print(json.dumps(s))


if __name__ == "__main__":
    main()
