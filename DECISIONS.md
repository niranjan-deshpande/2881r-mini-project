# Decisions

One line per non-obvious choice, with the reason. Newest at the bottom of each section.

## Setup
- Work lives in a new repo (`decomp/`); Agastya's and Juliana's repos are read-only inputs (cloned alongside). — Keeps their history clean; Niranjan OK'd a new repo.
- Layer index L = output of decoder block `layers[L]` (0-indexed). Verified: `build_dom.py` takes `hidden_states[1:]` (drops embeddings) and `t2_acts.py` hooks `lm.layers[L]`; both give the same tensor for L < 63. "Layer 40" is the 41st block. — Brief asked to confirm.
- Split: `md5(sample_id) % 2`, half 0 = selection, half 1 = held-out (exactly as `t2_analyze.py`). — Brief: reuse exactly.

## Sample sizes
- Fixed n, not adaptive: 300 hack pairs, 200 per candidate / baseline / general-cheating format. — Niranjan preferred a simple fixed rule; the Claude v_hack already has split-half ρ = 0.976 at n = 135 (c ≈ 3.4), so 200 pairs gives ρ ≈ 0.98 for a signal of that strength. Reliability is still reported per direction after the GPU pass.

## Nulls
- Label-shuffled DoMs use balanced sign flips within pairs (exactly half the pairs swapped), not coin flips. — With coin flips the ±1/√n imbalance leaks v: on the Claude pairs, coin-flip shuffles had |cos| ≈ 0.41 with v_hack.

## Generation (pending pilot)
- Generator chosen by a 3-arm pilot (GPT-6 Luna high effort / GPT-5.6 Terra / Claude Sonnet subagents), same prompts and seeds, blind-graded. Rule fixed before looking: pick the cheapest arm within ~5 points of the best on auto-check pass rate and contamination rate, and not noticeably more templated. — Brief fixed Terra, but the actual requirement is one generator for everything.

## Analysis code (`src/rhdecomp/`)
- Length control: one OLS fit of score on log(n_tokens) over all evaluation passages, not refit inside bootstrap resamples. — Conservative; also removes any hack signal that covaries with length.
- Peak decomposition centers each candidate on its mean over all tokens of clean passages; a peak is flagged as an opposite-sign cluster when two candidates of opposite sign each contribute ≥ 50% of the peak's elevation. — Threshold is a judgment call; reported as such.
- Max detector: z-score parameters and the "best single candidate" are chosen on the selection half, compared on held-out. — Data discipline.
- Odd n in split-half reliability: one pair dropped per split so halves are equal. — Keeps Spearman–Brown exact.

## Lenses
- Logit lens + native J-lens + native R-lens readouts for every direction, computed per direction by finite differences at L40 (no full Jacobian); J++ borrowed from the published Qwen3.6-27B lens (layer 40 is J++-fitted), reported only if it agrees with the native readouts. Native J++ refit skipped. — Full Jacobian fits cost 2–5 H100-h plus engineering; per-direction readouts cost ~5–15 GPU-min.
