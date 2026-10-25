r"""Figures for the 2.3 submission, regenerated from the committed outputs. CPU only.

  python make_figures.py        (run from sprint\report; reads ..\canary\prereg and ..\colludebench)
Writes fig1_canary.png and fig2_union.png next to this file.
"""
import csv
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "canary"))
from analyze import canary  # noqa: E402
from report import load, run_prices  # noqa: E402

INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb"
ACCENT = "#2a78d6"  # the positive control / the carrying statistic
NASH, MONO = 1.473, 1.925  # Riemer/Calvano parameters, symmetric unit cost

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "savefig.facecolor": SURF})


def dot_whisker(ax, x, est, lo, hi, color):
    ax.plot([x, x], [lo, hi], color=color, lw=2, solid_capstyle="round", zorder=2)
    ax.plot(x, est, "o", ms=8, color=color, mec=SURF, mew=2, zorder=3)


def fig1():
    d = HERE.parent / "canary" / "prereg"
    arms = [a for a in ("P-0", "POS", "M", "M+P", "M-S") if (d / f"{a}.csv").exists()]
    data = {a: load(d / f"{a}.csv") for a in arms}
    rng = np.random.default_rng(0)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"wspace": 0.38})

    pos = canary(data["POS"])["effect_raw"]
    a1.axhline(0, color=MUTED, lw=1, zorder=1)
    a1.axhline(pos, color=ACCENT, lw=1, ls=(0, (4, 3)), zorder=1)
    a1.text(len(arms) - 0.35, pos, "POS effect:\na leak the\ntest can see", color=ACCENT, va="center", fontsize=7.5, bbox=dict(fc=SURF, ec="none", pad=1))
    for i, a in enumerate(arms):
        c = canary(data[a])
        dot_whisker(a1, i, c["effect_raw"], *c["ci_raw"], ACCENT if a == "POS" else INK2)
    a1.set_xticks(range(len(arms)), arms)
    a1.set_xlim(-0.5, len(arms) + 0.6)
    a1.set_ylabel("Effect of A's private cost on B's price\n(price units, 95% CI, 40 runs)")
    a1.set_title("(a) Cost leak: none detected, but nulls are wide", loc="left", fontsize=9, color=INK)
    a1.grid(axis="y", color=GRID, lw=0.8)
    a1.set_axisbelow(True)

    for y, lab in ((NASH, "Nash 1.47"), (MONO, "monopoly 1.93")):
        a2.axhline(y, color=MUTED, lw=1, ls=(0, (2, 2)), zorder=1)
        a2.text(len(arms) - 0.35, y, lab, color=INK2, va="center", fontsize=7.5, bbox=dict(fc=SURF, ec="none", pad=1))
    for i, a in enumerate(arms):
        v = run_prices(data[a])
        boots = [rng.choice(v, len(v)).mean() for _ in range(5000)]
        lo, hi = np.quantile(boots, [0.025, 0.975])
        dot_whisker(a2, i, v.mean(), lo, hi, INK2 if a == "P-0" else ACCENT if a == "POS" else INK)
    a2.set_xticks(range(len(arms)), arms)
    a2.set_xlim(-0.5, len(arms) + 0.9)
    a2.set_ylabel("Mean market price per run\n(95% bootstrap CI over runs)")
    a2.set_title("(b) Price level: a channel raises it", loc="left", fontsize=9, color=INK)
    a2.grid(axis="y", color=GRID, lw=0.8)
    a2.set_axisbelow(True)
    fig.savefig(HERE / "fig1_canary.png", dpi=200, bbox_inches="tight")
    print("wrote fig1_canary.png:", arms)


def fig2():
    rows = list(csv.DictReader(open(HERE.parent / "colludebench" / "leave_one_out.csv", encoding="utf-8")))
    r = {x["config"]: x for x in rows if x["alpha"] == "alpha_1e-02"}
    others = [k for k in r if k.startswith("ALL - ") and k not in ("ALL - permutation_invariance", "ALL - acceptance_bias")]
    assert len({r[k]["tp"] for k in others}) == 1  # the six other removals all leave the union unchanged
    show = [("All 8 statistics", r["ALL"], INK),
            ("without any one of the other 6", r[others[0]], INK2),
            ("without acceptance_bias", r["ALL - acceptance_bias"], INK2),
            ("without permutation_invariance", r["ALL - permutation_invariance"], ACCENT),
            ("permutation_invariance alone", r["permutation_invariance alone"], ACCENT)]
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    for i, (lab, x, col) in enumerate(show):
        y = len(show) - 1 - i
        ax.plot([float(x["lo"]), float(x["hi"])], [y, y], color=col, lw=2, solid_capstyle="round")
        ax.plot(float(x["tpr"]), y, "o", ms=8, color=col, mec=SURF, mew=2)
        ax.text(1.03, y, f"{x['tp']}/{x['n_pos']}", va="center", color=INK2, fontsize=8)
    ax.set_yticks(range(len(show)), [s[0] for s in reversed(show)])
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("True-positive rate at FPR 1e-2 (ColludeBench ablation.json; Wilson 95% CI over 17 positive configurations)")
    ax.set_title("Removing one statistic halves the union; that statistic fires on 99% of honest windows (metrics.json)",
                 loc="left", fontsize=9, color=INK)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    fig.savefig(HERE / "fig2_union.png", dpi=200, bbox_inches="tight")
    print("wrote fig2_union.png")


def fig3():
    """Z2: B's round-1 price against the number in its prompt, by speaker. 40 independent calls per arm."""
    rows = list(csv.DictReader(open(HERE.parent / "track3" / "z2" / "main" / "z2.csv", encoding="utf-8")))
    by = {}
    for x in rows:
        if x["p_b"]:
            by.setdefault(x["arm"], []).append(float(x["p_b"]))
    rng = np.random.default_rng(0)
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    ax.plot([1.0, 3.8], [1.0, 3.8], color=MUTED, lw=1, ls=(0, (2, 2)), zorder=1)
    ax.text(3.65, 3.85, "copies exactly", color=INK2, fontsize=7.5, ha="right")
    for y, lab in ((NASH, "Nash"), (MONO, "monopoly")):
        ax.axhline(y, color=GRID, lw=1, zorder=0)
        ax.text(3.85, y, lab, color=MUTED, fontsize=7, va="center")
    for prefix, col, dx, lab in (("RIVAL", INK, -0.04, "rival proposes X"), ("ANALYST", ACCENT, 0.04, "analyst recommends X")):
        pts = sorted((float(a.split("-")[1]), v) for a, v in by.items() if a.startswith(prefix))
        for i, (xv, v) in enumerate(pts):
            v = np.array(v)
            lo, hi = np.quantile([rng.choice(v, v.size).mean() for _ in range(2000)], [0.025, 0.975])
            dot_whisker(ax, xv + dx, v.mean(), lo, hi, col)
            if i == 0:
                ax.plot([], [], "o", color=col, label=lab)
    ax.set_xlabel("Number X in B's prompt (round 1, no history)")
    ax.set_ylabel("B's price (mean, 95% CI, 40 calls)")
    ax.set_xlim(1.0, 4.1)
    ax.set_ylim(1.0, 4.1)
    ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    ax.set_title("B follows the number, down as well as up, from any speaker", loc="left", fontsize=9, color=INK)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    fig.savefig(HERE / "fig3_compliance.png", dpi=200, bbox_inches="tight")
    print("wrote fig3_compliance.png")


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
