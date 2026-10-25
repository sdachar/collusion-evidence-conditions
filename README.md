# What should count as evidence of AI collusion? (Apart AI Collusion Sprint, Track 2.3)

The repository has three parts:
- **Four conditions** for evidence of collusion, as executable checks: [`CONDITIONS.md`](CONDITIONS.md).
- **An audit of three published instruments** from their own released files: ColludeBench, the
  CoT-judge null of arXiv 2608.18078, and NARCBench.
- **A pre-registered randomised "canary" test** that passes all four conditions.

Report: `report/SUBMISSION.md` (the PDF is the submitted version).

**Results in one paragraph:**
- **Every condition that can be checked fails, and the placebo condition cannot be checked on any of
  the three instruments** from what they release.
  - ColludeBench's union falls from 15/17 to 7/17 without `permutation_invariance`, which fires on
    99% of honest windows. Its evaluation has one negative configuration.
  - The 2608.18078 null is over n = 7 points (CI [−0.65, +0.83]).
  - NARCBench's label equals the assigned role, and 8 of 31 positives did not coordinate by the
    authors' own flag.
- **The canary:** its positive control fires (+0.133 price units [+0.067, +0.198]) and its placebo
  does not. With messaging, LLM pricing agents raise prices by 1.1–1.4, past the monopoly price, without any profit gain (profit index Δ < 0 in M and M+P) and with no detectable cost leak.
  Both nulls are under-powered.
- **Lockstep is compliance, not collusion:**
  - **Round 1:** B copies A's number before any history exists (34/40 runs in M, 38/40 in M+P), at a
    cost of about 30 profit per round (`canary/compliance.py`).
  - **Pre-registered follow-up (Z2),** 40 calls per arm on self-hosted Qwen3.8-27B: B prices at the
    proposed number whether it is 1.20, below Nash (40/40 at ≤ 1.30), or 3.50 (40/40). It follows an
    analyst as closely as the rival (shift ratio 0.97 [0.91, 1.00]).

## Layout

| Path | What |
|---|---|
| `CONDITIONS.md` | The four conditions, thresholds, how to score a new instrument, current card |
| `conditions/` | `check_conditions.py` (numpy only), `build_specs.py`, `specs.json`, `card.txt`, 14 tests |
| `colludebench/` | `00_reproduce_one.py` (16/16 cells), `01_leave_one_out.py` → `leave_one_out.csv`, `GATE-K1.md` |
| `canary/` | Harness, estimator (`analyze.py`), runner, `report.py`, 16 tests |
| `canary/prereg/` | Every pre-registered arm: `<arm>.csv` (one row per round) and `<arm>.calls.jsonl` (every API call) |
| `PREREG-P9-canary.md`, `PREREG-HASHES.txt` | Pre-registration with dated amendments A1–A7; SHA-256 hashes stand in for commits |
| `report/` | `SUBMISSION.md`, `CARD.md`, `make_figures.py`, figures |
| `canary/gate-*` | Smoke tests before pre-registration. Excluded from every estimate (A2) |
| `canary/compliance.py` | Round-1 adoption, forgone profit, round-number share, from the stored arms (no API calls) |
| `track3/PREREG-Z2-anchor.md`, `track3/z2_anchor.py`, `track3/z2/` | The Z2 compliance follow-up: pre-registration (hash in `PREREG-Z2-HASH.txt`), code, data. `serve_qwen.py` serves the model on Modal |

## Reproduce

```
cd conditions; python -m pytest -q
cd canary;     python -m pytest -q
python report.py                       # every canary number, from prereg/*.csv
cd report;     python make_figures.py  # both figures, CPU only
```

- **Re-running an arm** needs a Groq key in `~/.groq_key`:
  `python run_canary.py --agents groq --runs 40 --arms M --out <dir> --seed 20261021`.
  Free-tier Groq allows about one arm per day (200k tokens/day).
- **Running offline, no key needed:** `python run_canary.py --agents scripted --arms P-0 POS M`.
- **The audit scripts read third-party files,** which are not redistributed here:
  - ColludeBench `results/experiments/{metrics,ablation}.json` (github.com/Ostailor/Steganographic_Collusion);
  - NARCBench `scenarios/` and `activations/qwen3_32b/core/metadata_gen.json`
    (huggingface.co/datasets/aaronrose227/narcbench, revision 19cb14b).

  Run them with `python -I`, and keep downloads in their own directory.

## Credit and scope

ColludeBench is MIT-licensed and ships its detector output. That is what made an arithmetic audit
possible, and its author deserves credit for it. Every finding concerns an instrument, never an
author.

These are small-scale testbeds for studying detection. No colluding agent is built or released.
