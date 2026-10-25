"""Condition (ii) on ColludeBench from its committed ablation.json: the full detector union vs the union
with each detector removed, at both FPR budgets. Every entry is 17 positive and 1 negative configuration
(see GATE-K1.md), so TPRs are k/17 and carry Wilson intervals over 17.
  python -I -X utf8 01_leave_one_out.py <ablation.json> [out.csv]
"""
import csv
import json
import math
import sys


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def main(path, out=None):
    a = json.load(open(path, encoding="utf-8"))
    full_key = max(a, key=lambda k: len(k.split(",")))
    dets = full_key.split(",")
    rows = []
    for alpha in ("alpha_1e-02", "alpha_1e-03"):
        configs = [("ALL", full_key)] + [(f"ALL - {d}", ",".join(x for x in dets if x != d)) for d in dets]
        configs += [(f"{d} alone", d) for d in dets]
        for label, key in configs:
            e = a[key][alpha]
            n = e["tp"] + e["fn"]
            lo, hi = wilson(e["tp"], n)
            rows.append({"alpha": alpha, "config": label, "tp": e["tp"], "n_pos": n, "tpr": e["tp"] / n,
                         "lo": lo, "hi": hi, "fp": e["fp"], "n_neg": e["fp"] + e["tn"]})
    for r in rows:
        print(f"{r['alpha']:12s} {r['config']:38s} TPR {r['tp']:2d}/{r['n_pos']} = {r['tpr']:.3f} "
              f"[{r['lo']:.2f}, {r['hi']:.2f}]  FP {r['fp']}/{r['n_neg']}")
    if out:
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)


if __name__ == "__main__":
    main(*sys.argv[1:3])
