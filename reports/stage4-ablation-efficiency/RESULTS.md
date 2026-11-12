# Stage-four results (course scope: fixed pilot 100 questions)

Ablation: 3500 successful slots. Efficiency complete: True; inspect coverage.json.

| Method | n | EM (%) | Delta vs NPU full (pp) | 95% CI (pp) |
| --- | ---: | ---: | ---: | --- |
| original | 500 | 84.6 | +2.0 | [-2.2, 7.0] |
| longllmlingua_2x | 500 | 82.6 | +0.0 | reference |
| longllmlingua_2x_no_coarse | 500 | 45.0 | -37.6 | [-47.2, -28.4] |
| longllmlingua_2x_no_fine | 500 | 81.2 | -1.4 | [-4.2, 1.2] |
| longllmlingua_2x_no_dynamic | 500 | 78.0 | -4.6 | [-8.6, -0.8] |
| longllmlingua_2x_no_restrict | 500 | 83.2 | +0.6 | [-2.2, 3.6] |
| longllmlingua_2x_reorder | 500 | 79.6 | -3.0 | [-7.2, 0.8] |
| longllmlingua_2x_no_recovery | 500 | 83.2 | +0.6 | [0.0, 1.6] |

Efficiency: 100 common samples before warmup; 99 measured samples/method.
Position distribution after warmup: {1: 19, 5: 20, 10: 20, 15: 20, 20: 20}.
Statistics use question-level paired bootstrap, 2000 draws, seed 42, all five positions retained.
Efficiency is matched by question AND position across all 12 methods; planned matrix complete: True.
No additional API calls. No monetary API cost inferred from token usage.
