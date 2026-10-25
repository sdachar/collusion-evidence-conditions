# Results: leniency for LLM cartels, the incentive ladder (portfolio project)

Run Sat 24 Oct 2026, 15:01–15:20 IST, per `PREREG-T3-leniency.md` (hash `75160875…5AC1`, 14:54).
- **Model:** Qwen3.8-27B (rev 1d4bf0f2), vLLM on a Modal A100-80GB.
- **Data:** `ladder/main/` (7 arms × 40 runs), `ladder/live/` (2 × 40), `ladder/pilot/` (exploratory,
  never pooled). Analysis: `python analyze_t3.py ladder/main --ladder`.
- **Parse failures:** 0. **The app was stopped after the run.**
- **Compute:** about 30 min of A100 in total (estimated $1.5–2; to be verified on the billing page).

## Headline

**Leniency does not break this LLM cartel, and the reason is a say-do gap.**
1. **Offered a report field with no authority behind it, B reports in 37/40 runs at the first
   chance (F0).**
2. **Once the consequences are spelled out, reporting falls to 1–7 of 40 and rises with what
   reporting pays** (rank correlation 0.82, R1 2.5% → R3-100 17.5%). **The pre-registered headline
   contrast is too small:** R3-50 − R1 = +0.10 [0.00, 0.225].
3. **B never files a false report** when there is nothing true to report (PLC 0/40).
4. **No regime moves prices.** B keeps pricing 1.90 in 100% of post-announcement rounds in every
   arm, and ~90% of reporters keep the cartel price the very next round.

Reporting is something the model *says*. It changes nothing it *does*.

## Per arm (firm B; scripted A says and prices 1.90; 40 runs each)

| Arm | First-round report (primary) | Any report | Verified | Snitch and stay | B at 1.90 before / after | B's price after |
|---|---|---|---|---|---|---|
| F0: field only, no authority | **37/40** | 40 | 40 | 40/40 | 1.00 / 1.00 | 1.90 |
| R1: reporter fined 100 | 1/40 | 11 | 11 | 10/11 | 1.00 / 1.00 | 1.90 |
| L28: proposer-only liability | 5/40 | 18 | 18 | 17/18 | 1.00 / 1.00 | 1.90 |
| R2: leniency | 4/40 | 15 | 15 | 13/15 | 1.00 / 1.00 | 1.90 |
| R3-50: leniency + 50 | 5/40 | 17 | 17 | 16/17 | 1.00 / 1.00 | 1.90 |
| R3-100: leniency + 100 | 7/40 | 22 | 22 | 20/22 | 1.00 / 1.00 | 1.90 |
| PLC: matched chatter, nothing to report | **0/40** | 0 | 0 | — | 0.49 / 0.77 | 1.90 (median) |

## Pre-registered predictions

| # | Prediction | Result |
|---|---|---|
| H1 | R3-50 − R1 first-round report rate ≥ 0.20, CI excluding 0 | **FAILS:** +0.10 [0.00, 0.225]. On any report: +0.15 [−0.05, +0.35] |
| H2 | F0 and R1 each < 10% | **FAILS on F0** (92.5%); R1 holds (2.5%). By the pre-registered rule (≥ 20%), **reporting is substantially compliance-driven** |
| H3 | Rates rise with payoff, R1 < L28 ≤ R2 < R3-50 ≤ R3-100 (descriptive) | **Mostly holds:** rank correlation 0.82. L28 (12.5%) sits slightly above R2 (10%), within noise |
| H4 | PLC false-report rate ≥ 10% | **FAILS:** 0/40. No false accusations |
| H5 | R3-100 ≥ R3-50 | **Holds** (7 vs 5 first-round; 22 vs 17 any), descriptive |
| H6 | > 50% of R2/R3 reporters keep pricing 1.90 next round | **Holds:** 49/54 (91%) |
| H7 | follow_post(L28) ≥ follow_post(R1) | **Holds trivially:** both 1.00. No arm moves price |
| Timing | Reports cluster at the first announced round | **Only in F0** (37 of 40 first reports at index 8). In the incentive arms, first reports spread across rounds 8–15 |

## Live-partner check (both firms LLM; descriptive; the cartel is not profitable)

| Arm | First-round report | Any report | Verified | B's price after |
|---|---|---|---|---|
| LIVE-R1 | 2/40 | 8 | 8 | 4.06 |
| LIVE-R3-50 | 4/40 | 17 | 16 | 4.92 |

- **The any-report contrast is +0.225 [+0.025, +0.425].** Reward raises reporting with a live
  partner too.
- **Caveat:** these LLM–LLM pairs priced at 4–6, far above monopoly (Δ ≈ −1.5 to −1.8). So reporting
  is not costly to them, and "snitch and stay" (defined at 1.90) does not apply.

## Reading
1. **The bare report field is the strongest "intervention".** With no authority, no fine and no
   reward, a reply field asking "report?" makes the model report its partner in 92.5% of first
   chances. Any leniency result on LLMs that lacks an F0-style control confuses the offer with the
   incentive.
2. **The incentive matters a little, in the right direction.** Spelling out costs and rewards
   suppresses reporting, and it then rises with the payoff (rank 0.82). But the pre-registered
   headline contrast misses its threshold. The honest summary is a weak incentive response on top of
   a large compliance effect.
3. **Reporting is decoupled from conduct.** No regime changes B's price; 91% of reporters keep the
   cartel price. For deployers, a self-report from an LLM agent is not evidence that it stopped. For
   the 2.3 conditions, this is emission vs action again.
4. **No false accusations** in the chatter placebo: the model does not invent coordination when
   there is no proposal to quote. Verification is by exact quote, so this measures attempts.

## Limits
- One model, one temperature, scripted partner, 16 rounds, 40 runs per arm.
- First-round reports are low-count (1–7/40) outside F0, so intervals are wide.
- Audits (15% a round) close cases, censoring later rounds; that is why first-round reporting is
  primary.
- The live check uses an unprofitable cartel.
