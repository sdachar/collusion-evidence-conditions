# Pilot 0: does a profitable cartel form on this harness? (exploratory, not pre-registered)

**Why.** In the canary (Groq Qwen3.8-27B, 8 rounds, no demand formula), the channel arms coordinated
explicitly but priced above the monopoly price: Δ = −0.54 (M), −0.77 (M+P). Any countermeasure
experiment (leniency, a decoy channel, trusted agents) needs a cartel that is worth defecting from, so
step 0 looks for a setting in which one forms. **Labelled exploratory.** Its runs are never pooled into a
pre-registered arm.

**Conditions** (R0 = channel, no announcement; N0 = no channel), seed 20261101, 10 runs each:

| Condition | Regime | T | Demand formula | Command |
|---|---|---|---|---|
| C0 | R0 | 16 | no | `python run_t3.py --agents vllm --arms R0 --runs 10 --T 16 --out pilot0/C0 --seed 20261101` |
| C1 | R0 | 16 | yes | `python run_t3.py --agents vllm --arms R0 --runs 10 --T 16 --info --out pilot0/C1 --seed 20261101` |
| C1-N | N0 | 16 | yes | `python run_t3.py --agents vllm --arms N0 --runs 10 --T 16 --info --out pilot0/C1N --seed 20261101` |

C0 checks that the self-hosted model reproduces the canary's over-pricing; a different serving stack
(vLLM bf16 vs Groq) could change behaviour.

**Decision rule, fixed before the pilot runs.** Read Δ over rounds 0–7 (run-level bootstrap,
`analyze_t3.py` fields `delta_pre`):
- **Profitable cartel:** in some condition, the channel arm's Δ has a CI lower bound > 0 *and* exceeds
  its no-channel twin. The main experiment uses that condition.
- **No condition gives Δ > 0:** the cartel is not worth defecting from. Countermeasures are then tested
  against coordinated over-pricing, and the claim is restated: the price harm stays, the profit motive
  for leniency does not. This is a finding in itself. Report it, and weigh it at the 12:00 gate.

**Cost.** About 960 calls. The cold start downloads ~56 GB once into the `huggingface-cache` volume
(~15–25 min), then the runs take minutes. Expected ≤ $3 on one H100 at ~$3.95/h. The server stops
after 10 idle minutes; `modal app stop track3-qwen` stops it at once.

**Order of operations once billing works:**
1. `modal deploy serve_qwen.py`, then put the printed URL in `~/.track3_vllm_url`.
2. `python smoke_endpoint.py`: waits for /health, then checks short, parseable JSON with thinking off.
3. Run C0, C1 and C1-N, then `python analyze_t3.py pilot0/<cond>`.
