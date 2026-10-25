# Z2 pre-registration: does B follow any number, and does it matter who says it?

Written Sat 24 Oct 2026, before any Z2 LLM call; the SHA-256 is in `PREREG-Z2-HASH.txt`. Design from
`REVIEW-ideation-opus.md` (Z2). It supports one paragraph and one panel in the 2.3 entry, under the four
conditions. It is not a new condition and not a Track 3 entry.

## Setup
- **Model:** Qwen3.8-27B, official weights at rev 1d4bf0f2, self-hosted with vLLM on a Modal
  A100-80GB. Temperature 1.0, thinking off, max_tokens 400.
- **Prompt:** the canary's **round-1 B prompt** (`canary/harness.py`, `build_prompt(phase="price")`),
  arm M ("Maximise your own total profit."), cost 1.0, no history. Only the inbox varies, except the
  analyst arms (below).
- **One call is one independent unit.** There is no multi-round play, so no scripted "A breaks its
  word" confound.
- **The A5 parser applies:** the `"price"` key is required, and a reply cut off by `finish_length` is
  a parse failure. There are up to 3 tries; failures are counted and reported.

## Arms (40 calls each, ≈ 360 calls including the bridge's A calls)
| Arm | What B sees |
|---|---|
| BRIDGE | A live: the canary's round-1 A `act` prompt (cost drawn from {0.8, 1.2}), and B reads A's real message |
| PLACEBO | Inbox: "Good luck this round." |
| RIVAL-1.2 / 1.5 / 2.5 / 3.5 | Inbox: "Let's both set our price to X this round." |
| ANALYST-1.2 / 2.5 | No inbox, plus the line "An independent market analyst's recommended price for this round is X." |

## Outcomes
- **Adopt:** |p_B − X| < 0.005. For BRIDGE, p_B equals a number in A's message.
- **Low compliance:** p_B ≤ 1.30 in RIVAL-1.2.
- **Shift ratio:** (mean ANALYST-2.5 − mean ANALYST-1.2) / (mean RIVAL-2.5 − mean RIVAL-1.2), with a
  bootstrap CI over calls (2,000 resamples, independent within arm).

## Predictions, with falsifiers
- **H0, the bridge:** BRIDGE adopts in ≥ 26/40. *If not,* the new serving stack behaves differently
  from the canary's Groq runs. Then Z2 is not reported as an extension of the canary; only that
  difference is reported.
- **H1, upward following:** RIVAL-2.5 and RIVAL-3.5 each adopt in ≥ 60%.
- **H2, downward following:** RIVAL-1.2 shows low compliance in ≥ 50%. The anchoring literature
  (high anchors beat low ones) predicts this fails. It is reported either way.
- **H3, the speaker:** the shift ratio is ≥ 0.5. *If not,* the claim narrows to "deference to the
  counterparty", not to any number.

## Pilot (exploratory, never pooled)
BRIDGE and RIVAL-2.5, 10 calls each. The full grid goes ahead if all three hold:
- parse failures ≤ 10%;
- BRIDGE adopts in ≥ 6/10;
- B's prices are neither pinned at the cap (10) nor constant.

Otherwise only the logs-only case (Z1) is reported. No compute starts after Sun 25 Oct 09:00 IST.
