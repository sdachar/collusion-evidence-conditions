import json, sys
m = json.load(open(sys.argv[1], encoding="utf-8"))["detectors"]
d = m["cross_run_mi"]
print("pos[0]", d["positives"][0], "neg[0]", d["negatives"][0])
print("alphas", json.dumps(d["alphas"], indent=0)[:600])
for k in ("acceptance_bias", "detector_union_bonferroni"):
    print(k, "pos", m[k]["positives"][:3], "neg", m[k]["negatives"][:3]); print(json.dumps(m[k]["alphas"])[:500])
print(json.dumps(m["detector_union"]["rejections"])[:800])
