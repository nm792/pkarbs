# RBOB signal rule, locked test (EIA NY Harbor spot through 3 Nov)
| series | strikes (events) | hit | implied | gap |
|---|---:|---:|---:|---:|
| KXAAAGASD | 89 (55) | 53.9% | 50.5% | -1.2c |
| KXAAAGASDCA | 124 (46) | 60.5% | 48.8% | -15.1c |
| KXAAAGASDTX | 182 (50) | 54.9% | 52.0% | -16.9c |
| KXAAAGASDFL | 163 (40) | 45.4% | 50.5% | -30.9c |
| KXAAAGASDNY | 102 (40) | 45.1% | 48.5% | -26.2c |
| KXAAAGASDIL | 151 (42) | 55.0% | 50.5% | -20.6c |
| KXAAAGASDNJ | 136 (52) | 44.9% | 50.2% | -28.8c |
| KXAAAGASDWA | 160 (48) | 51.9% | 49.8% | -20.8c |
| KXAAAGASDNC | 151 (48) | 53.0% | 50.5% | -18.9c |
| KXAAAGASDOH | 151 (40) | 51.7% | 50.6% | -24.5c |
| KXAAAGASDPA | 140 (48) | 46.4% | 51.2% | -27.5c |
| KXAAAGASDGA | 152 (50) | 57.2% | 50.2% | -19.8c |
| KXAAAGASDVA | 160 (48) | 52.5% | 51.2% | -22.0c |

train: 915 strikes, 238 events: hit 46.6% vs implied 50.1%, gap -24.22c (95% CI -29.08, -19.00), placebo z -1.4, size/strike $4, $-23/day over 22d -> FAIL/UNPROVEN
TEST: 946 strikes, 369 events: hit 56.9% vs implied 50.7%, gap -18.90c (95% CI -23.20, -14.79), placebo z +2.9, size/strike $16, $-48/day over 37d -> FAIL/UNPROVEN
POOLED: 1861 strikes, 607 events: hit 51.8% vs implied 50.4%, gap -21.52c (95% CI -24.89, -17.99), placebo z +0.8, size/strike $10, $-38/day over 60d -> FAIL/UNPROVEN
