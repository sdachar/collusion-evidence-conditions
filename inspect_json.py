import json, sys
m = json.load(open(sys.argv[1], encoding="utf-8"))
def sk(x, d=0, maxd=3):
    if d > maxd: return
    if isinstance(x, dict):
        for k, v in list(x.items())[:14]:
            desc = type(v).__name__ + (f"[{len(v)}]" if isinstance(v, (list, dict)) else f"={v!r}"[:60])
            print("  " * d + f"{k}: {desc}")
            sk(v, d + 1, maxd)
        if len(x) > 14: print("  " * d + f"... +{len(x)-14} keys")
    elif isinstance(x, list) and x:
        print("  " * d + f"[0] of {len(x)}:"); sk(x[0], d + 1, maxd)
sk(m)
