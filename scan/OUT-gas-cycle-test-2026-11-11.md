# Price-cycle rule, locked test
| state | strikes (events) | hit rate | market-implied | gap net of fee |
|---|---:|---:|---:|---:|
| OH | 29 (9) | 65.5% | 54.9% | -8.3c |
| MI | 13 (5) | 100.0% | 53.5% | +17.7c |
| IN | 11 (3) | 90.9% | 45.2% | +14.0c |
| WI | 0 qualifying | | | |

train: 32 strikes, 9 events: hit 68.8% vs implied 52.5%, gap -4.09c (95% CI -34.96, +22.73), placebo z +1.1, size/strike $1, $2/day over 11 days
TEST: 21 strikes, 8 events: hit 95.2% vs implied 52.5%, gap +13.02c (95% CI +6.32, +21.12), placebo z +2.3, size/strike $0, $0/day over 34 days
VERDICT: FAIL / UNPROVEN
