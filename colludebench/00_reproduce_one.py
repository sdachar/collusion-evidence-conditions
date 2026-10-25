"""Tue-20 gate (K1): reproduce metrics.md numbers from the committed metrics.json alone.

Recomputes TPR/FPR per single detector from the stored score lists and stored thresholds, using the
repo's own rule (auditor/metrics.py `_is_suspicious`: value > thr, `<` for permutation_invariance).
Run untrusted-data-safe:  python -I 00_reproduce_one.py <path to metrics.json>
"""
import json
import sys

LOWER_TAIL = {"permutation_invariance"}


def rates(pos, neg, thr, lower):
    hit = (lambda v: v < thr) if lower else (lambda v: v > thr)
    return sum(map(hit, pos)) / len(pos), sum(map(hit, neg)) / len(neg)


def main(path):
    dets = json.load(open(path, encoding="utf-8"))["detectors"]
    ok = True
    for name, d in dets.items():
        if not d["positives"] or not d["negatives"]:
            continue  # unions store only the summary; their recompute is tier 1 work
        for alpha, rep in d["alphas"].items():
            if rep["threshold"] is None:
                continue
            tpr, fpr = rates(d["positives"], d["negatives"], rep["threshold"], name in LOWER_TAIL)
            match = abs(tpr - rep["tpr"]) < 1e-12 and abs(fpr - rep["fpr"]) < 1e-12
            ok &= match
            print(f"{name:26s} a={alpha:6s} n+={len(d['positives']):6d} n-={len(d['negatives']):6d} "
                  f"TPR {tpr:.4f} (rep {rep['tpr']:.4f})  FPR {fpr:.5f} (rep {rep['fpr']:.5f})  {'OK' if match else 'MISMATCH'}")
    print("ALL MATCH" if ok else "SOME MISMATCH")


if __name__ == "__main__":
    main(sys.argv[1])
