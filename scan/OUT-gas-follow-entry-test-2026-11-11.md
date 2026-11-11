# Follow rule: later entry and early exit, locked grid (Bonferroni lower bound = 99.17% interval; windows A=latest 30 events, B=prior 30)
Strikes loaded: 4404

| entry (UTC ~) | window | strikes (events) | followed-side hit vs implied | mean spread | median $ traded next 2h per strike | hold gap (lo99) | exit-3h gap (lo99) | hold $/day | exit $/day | z hold / exit |
|---|---|---|---|---:|---:|---|---|---:|---:|---|
| 14Z | A | 1182 (616) | 58.5% vs 50.4% | 29.3c | $0 | -7.9c (-12.7) | -24.3c (-27.6) | $-4 | $-40 | +4.5 / +3.5 |
| 14Z | B | 949 (233) | 61.5% vs 50.7% | 53.8c | $0 | -17.0c (-23.4) | -45.5c (-50.7) | $6 | $-19 | +4.1 / +4.0 |
| 14Z | A+B | 2131 (849) | 59.9% vs 50.5% | 40.2c | $0 | -12.0c (-16.2) | -33.7c (-36.9) | $2 | $-59 | +6.1 / +5.5 |
| 19Z | A | 737 (532) | 53.5% vs 50.4% | 27.8c | $0 | -12.2c (-17.6) | -26.8c (-30.8) | $-23 | $-42 | +1.4 / +0.5 |
| 19Z | B | 731 (244) | 51.6% vs 50.9% | 43.6c | $0 | -22.3c (-28.7) | -41.7c (-46.1) | $-69 | $-77 | +0.3 / +1.5 |
| 19Z | A+B | 1468 (776) | 52.5% vs 50.7% | 35.7c | $0 | -17.3c (-21.5) | -34.2c (-36.9) | $-92 | $-120 | +1.1 / +1.5 |
| 01Z | A | 398 (324) | 46.2% vs 49.3% | 25.3c | $3 | -17.1c (-24.8) | -25.0c (-29.8) | $-20 | $-18 | -1.1 / +1.3 |
| 01Z | B | 407 (203) | 46.4% vs 51.7% | 41.3c | $0 | -27.1c (-35.1) | -45.9c (-49.9) | $-54 | $-69 | -1.8 / -0.4 |
| 01Z | A+B | 805 (527) | 46.3% vs 50.5% | 33.4c | $1 | -22.2c (-27.3) | -35.6c (-38.9) | $-73 | $-87 | -2.2 / +0.8 |

Verdict per combination (PASS needs both windows: gap>0, Bonferroni lower bound>0, >=100 strikes, >=40 events; pooled z>=2):
- entry 14Z, hold: FAIL/UNPROVEN
- entry 14Z, exit-3h: FAIL/UNPROVEN
- entry 19Z, hold: FAIL/UNPROVEN
- entry 19Z, exit-3h: FAIL/UNPROVEN
- entry 01Z, hold: FAIL/UNPROVEN
- entry 01Z, exit-3h: FAIL/UNPROVEN

By state (all windows pooled, followed side), entry 14Z / 19Z / 01Z: hit - implied, mean spread, hold gap
| state | 14Z | 19Z | 01Z |
|---|---|---|---|
| AK | n=82: -1.5c, sp 41c, gap -23.1c | n=54: +3.7c, sp 45c, gap -20.2c | n=34: -1.7c, sp 40c, gap -22.8c |
| AL | n=24: +20.5c, sp 18c, gap +10.0c | n=10: +32.4c, sp 20c, gap +20.7c | n=9: -20.6c, sp 19c, gap -31.4c |
| AR | n=32: +14.4c, sp 28c, gap -1.1c | n=19: +18.7c, sp 33c, gap +1.1c | n=10: +17.3c, sp 26c, gap +3.0c |
| AZ | n=159: +15.6c, sp 47c, gap -9.1c | n=117: +9.9c, sp 38c, gap -10.5c | n=75: +6.5c, sp 38c, gap -13.9c |
| CO | n=132: +9.1c, sp 57c, gap -20.2c | n=113: -17.4c, sp 53c, gap -44.7c | n=53: -17.6c, sp 50c, gap -43.8c |
| CT | n=68: +12.0c, sp 58c, gap -17.7c | n=36: -8.9c, sp 37c, gap -28.5c | n=22: -6.5c, sp 37c, gap -26.2c |
| DE | n=49: -9.2c, sp 27c, gap -24.3c | n=22: -19.0c, sp 22c, gap -31.5c | n=8: -32.6c, sp 20c, gap -44.2c |
| HI | n=50: -4.4c, sp 38c, gap -24.9c | n=40: +2.4c, sp 39c, gap -18.4c | n=22: +2.5c, sp 35c, gap -16.4c |
| IA | n=50: +9.5c, sp 26c, gap -5.1c | n=30: -3.9c, sp 39c, gap -24.6c | n=15: -16.8c, sp 40c, gap -37.9c |
| ID | n=34: +13.8c, sp 29c, gap -2.1c | n=24: +6.3c, sp 27c, gap -8.5c | n=19: +1.8c, sp 20c, gap -9.9c |
| KS | n=29: -11.6c, sp 27c, gap -26.2c | n=21: -8.6c, sp 32c, gap -25.7c | n/a |
| KY | n=29: +2.2c, sp 29c, gap -13.5c | n=16: +0.6c, sp 34c, gap -17.9c | n=8: -20.5c, sp 32c, gap -37.7c |
| LA | n=34: +32.2c, sp 27c, gap +17.3c | n=13: +30.2c, sp 19c, gap +19.2c | n/a |
| MA | n=99: +2.3c, sp 51c, gap -24.5c | n=82: +0.6c, sp 39c, gap -20.1c | n=40: -3.3c, sp 40c, gap -24.3c |
| MD | n=109: +7.2c, sp 46c, gap -16.9c | n=75: +5.4c, sp 35c, gap -13.6c | n=42: -6.5c, sp 33c, gap -24.5c |
| ME | n=17: +15.2c, sp 27c, gap +0.2c | n=18: +0.6c, sp 26c, gap -13.6c | n=9: +4.7c, sp 18c, gap -5.7c |
| MN | n=128: +8.4c, sp 49c, gap -17.3c | n=83: +7.1c, sp 43c, gap -15.6c | n=49: +2.0c, sp 35c, gap -17.0c |
| MO | n=101: +13.0c, sp 44c, gap -10.2c | n=62: +9.5c, sp 37c, gap -10.4c | n=35: -2.4c, sp 28c, gap -17.9c |
| MS | n=24: +13.8c, sp 21c, gap +2.0c | n=11: +31.8c, sp 26c, gap +17.4c | n/a |
| MT | n=38: +8.8c, sp 22c, gap -3.7c | n=27: +0.8c, sp 27c, gap -14.0c | n=11: +13.9c, sp 27c, gap -0.9c |
| ND | n=27: +15.3c, sp 19c, gap +4.3c | n=12: +11.4c, sp 13c, gap +3.3c | n/a |
| NE | n=48: +20.2c, sp 16c, gap +10.9c | n=39: +9.9c, sp 34c, gap -8.4c | n=11: -0.8c, sp 21c, gap -12.6c |
| NH | n=14: +9.6c, sp 31c, gap -7.3c | n=23: +1.7c, sp 18c, gap -8.9c | n/a |
| NM | n=64: +23.4c, sp 39c, gap +2.5c | n=39: +16.5c, sp 28c, gap +1.2c | n=15: +12.7c, sp 31c, gap -4.2c |
| NV | n=103: +10.7c, sp 56c, gap -18.3c | n=80: -5.7c, sp 40c, gap -27.0c | n=45: -9.2c, sp 39c, gap -29.9c |
| OK | n=41: +16.2c, sp 25c, gap +2.1c | n=23: -7.7c, sp 21c, gap -19.5c | n=15: -25.0c, sp 22c, gap -37.6c |
| OR | n=81: +17.1c, sp 41c, gap -4.6c | n=80: +5.3c, sp 38c, gap -15.0c | n=54: +0.5c, sp 34c, gap -17.7c |
| RI | n=17: +20.8c, sp 21c, gap +8.9c | n=10: +17.8c, sp 18c, gap +7.4c | n/a |
| SC | n=118: +12.0c, sp 45c, gap -11.8c | n=72: -2.1c, sp 33c, gap -19.7c | n=47: -22.7c, sp 38c, gap -43.3c |
| SD | n=36: +6.1c, sp 20c, gap -5.4c | n=32: -12.6c, sp 27c, gap -27.5c | n=11: -25.7c, sp 7c, gap -30.8c |
| TN | n=150: +6.9c, sp 48c, gap -18.0c | n=91: -1.7c, sp 35c, gap -20.3c | n=60: -2.9c, sp 35c, gap -21.5c |
| UT | n=47: -8.6c, sp 28c, gap -23.9c | n=29: +15.2c, sp 33c, gap -2.6c | n=18: +1.0c, sp 25c, gap -13.2c |
| VT | n=9: +11.4c, sp 17c, gap +1.6c | n=12: -9.8c, sp 17c, gap -19.6c | n/a |
| WV | n=35: +2.3c, sp 22c, gap -10.3c | n=19: +9.0c, sp 16c, gap -0.3c | n=8: +27.1c, sp 21c, gap +14.9c |
| WY | n=53: +4.0c, sp 22c, gap -8.7c | n=34: +0.6c, sp 31c, gap -16.1c | n=23: +2.3c, sp 29c, gap -13.6c |
