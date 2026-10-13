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
