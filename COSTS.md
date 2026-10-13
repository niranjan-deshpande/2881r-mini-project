# Costs

Caps: $60 RunPod, $80 OpenAI + OpenRouter combined. Budget is a cap, not a target.

## Prices (checked 2026-10-13, OpenRouter live model list; matches OpenAI's announced prices)
| Model | $/M in | $/M out | Batch |
|---|---|---|---|
| GPT-5.6 Terra | 2.00 | 12.00 | 1.00 / 6.00 |
| GPT-6 Luna | 0.10 | 0.50 | 0.05 / 0.25 |
| GPT-6 Sol | 2.00 | 10.00 | 1.00 / 5.00 |
| DeepSeek V4 Pro (OpenRouter) | 0.42 | 0.83 | – |
| DeepSeek V4.1 Flash (OpenRouter) | 0.04 | 0.77 | – |
| Claude Haiku 5.5 (OpenRouter) | 0.10 | 0.50 | 0.05 / 0.25 |

## Baselines
- OpenRouter key lifetime usage before this project: $25.05 (2026-10-13). Our OpenRouter spend = usage − 25.05.
- OpenAI: track via per-request `usage` fields logged by our scripts (and the dashboard).

## Log
| Date | Item | Provider | Cost |
|---|---|---|---|
| 2026-10-13 | CHECKPOINT 0 (all CPU) | – | $0.00 |
| 2026-10-13 | CP A: Luna generation pilots (smoke, v1, v2, v3, samples for all directions) | OpenAI | $1.62 |
| 2026-10-13 | CP A: Phase 2 rubric pilots, Luna side (full-transcript ×2, diagnostics, focused/snippet stages) | OpenAI | $0.46 |
| 2026-10-13 | CP A: contamination judging + Phase 2 pilots, Haiku side | OpenRouter | $1.27 |

**Running totals:** RunPod $0.00 · OpenAI $2.07 · OpenRouter $1.27 · **API total $3.34 of $80**
