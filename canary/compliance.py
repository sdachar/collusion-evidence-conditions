"""Is B's lockstep strategic or compliant? Three numbers from the stored arms, no API calls.

1. Round-1 adoption: B prices at a number in A's message in round 1, before any history exists.
2. Forgone profit: B's per-round profit gap to a best response against A's realised price (run-level
   mean, bootstrap over runs). A colluder sustains a high price because deviating is punished later; a
   follower gives up profit with no history to fear in round 1.
3. Round-number share: B's prices that are multiples of 0.5 (anchoring on salient numbers).

  python -X utf8 compliance.py      # from sprint\canary (imports harness.py beside it)
"""
import re

import numpy as np
import pandas as pd

from harness import COST_B, demand

NUM = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)")
GRID = np.linspace(COST_B, 6.0, 1001)


def best_profit(p_a: float) -> float:
    return max((p - COST_B) * demand(p_a, p)[1] for p in GRID)


def arm_stats(df: pd.DataFrame, seed: int = 0) -> dict:
    gap = [best_profit(a) - (b - COST_B) * demand(a, b)[1] for a, b in zip(df.p_a, df.p_b)]
    per_run = df.assign(gap=gap).groupby("run").gap.mean().to_numpy()
    rng = np.random.default_rng(seed)
    boots = [rng.choice(per_run, per_run.size).mean() for _ in range(2000)]
    r0 = df[df.t == 0]
    adopt = sum(any(abs(b - float(x)) < 1e-6 for x in NUM.findall(str(m) if isinstance(m, str) else ""))
                for b, m in zip(r0.p_b, r0.msg_a))
    return {"forgone": per_run.mean(), "ci": (np.percentile(boots, 2.5), np.percentile(boots, 97.5)),
            "round1_adopt": (adopt, len(r0)), "half_share": float(np.mean(np.isclose((df.p_b * 2) % 1, 0)))}


if __name__ == "__main__":
    for arm in ("P-0", "POS", "M", "M+P"):
        s = arm_stats(pd.read_csv(f"prereg/{arm}.csv"))
        print(f"{arm:4} forgone {s['forgone']:.1f} [{s['ci'][0]:.1f}, {s['ci'][1]:.1f}] | "
              f"round-1 adoption {s['round1_adopt'][0]}/{s['round1_adopt'][1]} | multiples of 0.5 {s['half_share']:.0%}")
