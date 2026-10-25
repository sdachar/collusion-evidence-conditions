import json, sys
a = json.load(open(sys.argv[1], encoding="utf-8"))
def walk(x, path=""):
    if isinstance(x, dict):
        if {"tp", "fn", "tn"} <= set(x):
            yield path, x["tp"], x["fn"], x.get("fp"), x["tn"]
        for k, v in x.items(): yield from walk(v, f"{path}/{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x): yield from walk(v, f"{path}[{i}]")
rows = list(walk(a))
print(len(rows), "entries; distinct (tp+fn, fp+tn):", sorted({(tp + fn, (fp or 0) + tn) for _, tp, fn, fp, tn in rows}))
for r in rows[:4]: print(r)
