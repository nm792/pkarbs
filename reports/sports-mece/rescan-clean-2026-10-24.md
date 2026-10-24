# rescan-clean-2026-10-24 — clean rescan (book resets, crossed books, dedup, per-run, rebates)

From: server agent, 24 Oct 2026, executing TASK-rescan-clean. Shadow mode only; no orders, no wallet keys; public endpoints only. v2 logger on shadow/data-v2/ untouched.

## Rescan (shadow/rescan-clean/runs.jsonl)
Command: `python3 shadow/rescan.py --data <rescan-data> --out shadow/rescan-clean/ --fetch-totals --gap-s 5 --max-taker-rebate 0.5`
- Runs written: 879, deduped to **771** (108 duplicate (event, side, t0) removed). Zero duplicates after dedup.
- Sides: yes 479, no 292. All runs carry px0, fee0, edge_full_fee.
- edge_full_fee: 0 = 376, 1 = 395 (the relaxed threshold at max_taker_rebate 0.5 added 376 runs that are not positive at the full fee).
- Book resets at gaps: **35 resets, 7,443.8 s skipped** (receive-time jumps > 5 s).
- Crossed-book checks rejected: 0 (no run opened on a crossed book).
- Hours covered: 17 (2026102311 .. 2026102405), missing 01Z, 04Z, 06Z (corrupt, excluded).
- rebate_rate: older events.jsonl lines lack it; filled 0.15 for sports legs with fee_rate 0.05 (change 7).

## Trade prints (change 10) — last_trade_price messages per raw hour
11Z 71, 12Z 99, 13Z 136, 14Z 295, 15Z 536, 16Z 1154, 17Z 1386, 18Z 2253, 19Z 3837, 20Z 4223, 21Z 497, 22Z 906, 23Z 918, 00Z 945, 02Z 973, 03Z 460, 05Z 789. Total 19,478. (A later resting-order sim is feasible.)

## Simulator outputs (as printed)
### usdc, cooldown 10 (R=0)
```
side=yes delay=0 runs=479 below_min=401 seen=$73.14 sim=$-302.11 unwind=$-328.43 worst=$-164.31 full=5 partial=14 none=0 cooldown_skip=9 fees=$55.18 wv=$817.50
side=yes delay=1 runs=479 below_min=401 seen=$73.14 sim=$-352.88 unwind=$-377.01 worst=$-222.84 full=1 partial=18 none=0 cooldown_skip=9 fees=$48.48 wv=$688.19
side=yes delay=3 runs=479 below_min=401 seen=$73.14 sim=$-84.68 unwind=$-84.68 worst=$-19.30 full=0 partial=12 none=7 cooldown_skip=9 fees=$27.56 wv=$287.04
side=yes delay=market runs=479 below_min=401 seen=$73.14 sim=$-352.88 unwind=$-377.01 worst=$-222.84 full=1 partial=18 none=0 cooldown_skip=9 fees=$48.48 wv=$688.19
side=no delay=0 runs=292 below_min=190 seen=$55.14 sim=$-611.69 unwind=$-633.15 worst=$-229.03 full=5 partial=24 none=3 cooldown_skip=12 fees=$48.29 wv=$639.90
side=no delay=1 runs=292 below_min=190 seen=$55.14 sim=$-548.46 unwind=$-548.89 worst=$-187.74 full=0 partial=27 none=5 cooldown_skip=12 fees=$42.38 wv=$471.41
side=no delay=3 runs=292 below_min=190 seen=$55.14 sim=$-528.66 unwind=$-528.83 worst=$-190.60 full=1 partial=24 none=7 cooldown_skip=12 fees=$36.70 wv=$421.64
side=no delay=market runs=292 below_min=190 seen=$55.14 sim=$-548.46 unwind=$-548.89 worst=$-187.74 full=0 partial=27 none=5 cooldown_skip=12 fees=$42.38 wv=$471.41
side=both delay=0 seen=$128.28 sim=$-913.80 unwind=$-961.58 fees=$103.46 wv=$1457.40
side=both delay=1 seen=$128.28 sim=$-901.34 unwind=$-925.90 fees=$90.85 wv=$1159.60
side=both delay=3 seen=$128.28 sim=$-613.34 unwind=$-613.51 fees=$64.26 wv=$708.68
side=both delay=market seen=$128.28 sim=$-901.34 unwind=$-925.90 fees=$90.85 wv=$1159.60
```

### usdc, cooldown 0 (R=0)
```
side=yes delay=0 runs=479 below_min=401 seen=$109.92 sim=$-345.58 unwind=$-383.53 worst=$-164.31 full=9 partial=19 none=0 cooldown_skip=0 fees=$72.32 wv=$1073.59
side=yes delay=1 runs=479 below_min=401 seen=$109.92 sim=$-420.09 unwind=$-444.21 worst=$-222.84 full=1 partial=27 none=0 cooldown_skip=0 fees=$63.51 wv=$852.41
side=yes delay=3 runs=479 below_min=401 seen=$109.92 sim=$-140.61 unwind=$-140.61 worst=$-19.30 full=0 partial=21 none=7 cooldown_skip=0 fees=$41.88 wv=$441.80
side=yes delay=market runs=479 below_min=401 seen=$109.92 sim=$-420.09 unwind=$-444.21 worst=$-222.84 full=1 partial=27 none=0 cooldown_skip=0 fees=$63.51 wv=$852.41
side=no delay=0 runs=292 below_min=190 seen=$80.72 sim=$-617.26 unwind=$-659.47 worst=$-229.03 full=10 partial=29 none=4 cooldown_skip=1 fees=$70.53 wv=$1004.10
side=no delay=1 runs=292 below_min=190 seen=$80.72 sim=$-579.07 unwind=$-579.91 worst=$-187.74 full=1 partial=35 none=7 cooldown_skip=1 fees=$59.58 wv=$645.43
side=no delay=3 runs=292 below_min=190 seen=$80.72 sim=$-568.72 unwind=$-568.89 worst=$-190.60 full=1 partial=31 none=11 cooldown_skip=1 fees=$46.60 wv=$521.67
side=no delay=market runs=292 below_min=190 seen=$80.72 sim=$-579.07 unwind=$-579.91 worst=$-187.74 full=1 partial=35 none=7 cooldown_skip=1 fees=$59.58 wv=$645.43
side=both delay=0 seen=$190.64 sim=$-962.84 unwind=$-1042.99 fees=$142.85 wv=$2077.69
side=both delay=1 seen=$190.64 sim=$-999.16 unwind=$-1024.12 fees=$123.08 wv=$1497.84
side=both delay=3 seen=$190.64 sim=$-709.33 unwind=$-709.50 fees=$88.49 wv=$963.47
side=both delay=market seen=$190.64 sim=$-999.16 unwind=$-1024.12 fees=$123.08 wv=$1497.84
```

### shares, cooldown 10 (R=0)
```
side=yes delay=0 runs=479 below_min=11 seen=$182.69 sim=$-536.67 unwind=$-603.01 worst=$-164.31 full=41 partial=83 none=2 cooldown_skip=118 fees=$112.41 wv=$1626.91
side=yes delay=1 runs=479 below_min=11 seen=$182.69 sim=$-504.03 unwind=$-558.83 worst=$-222.84 full=12 partial=104 none=10 cooldown_skip=118 fees=$86.46 wv=$1207.11
side=yes delay=3 runs=479 below_min=11 seen=$182.69 sim=$-245.87 unwind=$-257.11 worst=$-29.11 full=6 partial=102 none=18 cooldown_skip=118 fees=$63.17 wv=$729.70
side=yes delay=market runs=479 below_min=11 seen=$182.69 sim=$-504.03 unwind=$-558.83 worst=$-222.84 full=12 partial=104 none=10 cooldown_skip=118 fees=$86.46 wv=$1207.11
side=no delay=0 runs=292 below_min=16 seen=$55.79 sim=$-632.64 unwind=$-649.20 worst=$-229.03 full=30 partial=65 none=3 cooldown_skip=36 fees=$51.24 wv=$647.25
side=no delay=1 runs=292 below_min=16 seen=$55.79 sim=$-557.54 unwind=$-560.45 worst=$-187.74 full=10 partial=82 none=6 cooldown_skip=36 fees=$46.28 wv=$514.34
side=no delay=3 runs=292 below_min=16 seen=$55.79 sim=$-539.79 unwind=$-540.37 worst=$-190.60 full=8 partial=78 none=12 cooldown_skip=36 fees=$41.57 wv=$472.83
side=no delay=market runs=292 below_min=16 seen=$55.79 sim=$-557.54 unwind=$-560.45 worst=$-187.74 full=10 partial=82 none=6 cooldown_skip=36 fees=$46.28 wv=$514.34
side=both delay=0 seen=$238.48 sim=$-1169.32 unwind=$-1252.20 fees=$163.65 wv=$2274.16
side=both delay=1 seen=$238.48 sim=$-1061.57 unwind=$-1119.28 fees=$132.75 wv=$1721.45
side=both delay=3 seen=$238.48 sim=$-785.66 unwind=$-797.48 fees=$104.74 wv=$1202.53
side=both delay=market seen=$238.48 sim=$-1061.57 unwind=$-1119.28 fees=$132.75 wv=$1721.45
```

### shares, cooldown 0 (R=0)
```
side=yes delay=0 runs=479 below_min=11 seen=$361.33 sim=$-727.32 unwind=$-891.67 worst=$-164.31 full=84 partial=157 none=3 cooldown_skip=0 fees=$209.42 wv=$3098.06
side=yes delay=1 runs=479 below_min=11 seen=$361.33 sim=$-752.48 unwind=$-835.91 worst=$-222.84 full=18 partial=209 none=17 cooldown_skip=0 fees=$162.07 wv=$2116.28
side=yes delay=3 runs=479 below_min=11 seen=$361.33 sim=$-493.43 unwind=$-519.77 worst=$-29.11 full=12 partial=203 none=29 cooldown_skip=0 fees=$127.35 wv=$1516.07
side=yes delay=market runs=479 below_min=11 seen=$361.33 sim=$-752.48 unwind=$-835.91 worst=$-222.84 full=18 partial=209 none=17 cooldown_skip=0 fees=$162.07 wv=$2116.28
side=no delay=0 runs=292 below_min=16 seen=$94.57 sim=$-644.57 unwind=$-692.67 worst=$-229.03 full=41 partial=87 none=4 cooldown_skip=2 fees=$82.72 wv=$1166.87
side=no delay=1 runs=292 below_min=16 seen=$94.57 sim=$-617.36 unwind=$-621.15 worst=$-187.74 full=12 partial=111 none=9 cooldown_skip=2 fees=$70.15 wv=$757.86
side=no delay=3 runs=292 below_min=16 seen=$94.57 sim=$-612.62 unwind=$-613.25 worst=$-190.60 full=8 partial=106 none=18 cooldown_skip=2 fees=$54.96 wv=$608.32
side=no delay=market runs=292 below_min=16 seen=$94.57 sim=$-617.36 unwind=$-621.15 worst=$-187.74 full=12 partial=111 none=9 cooldown_skip=2 fees=$70.15 wv=$757.86
side=both delay=0 seen=$455.90 sim=$-1371.89 unwind=$-1584.34 fees=$292.13 wv=$4264.93
side=both delay=1 seen=$455.90 sim=$-1369.84 unwind=$-1457.06 fees=$232.22 wv=$2874.14
side=both delay=3 seen=$455.90 sim=$-1106.04 unwind=$-1133.03 fees=$182.31 wv=$2124.39
side=both delay=market seen=$455.90 sim=$-1369.84 unwind=$-1457.06 fees=$232.22 wv=$2874.14
```

### Rebate runs (usdc, cooldown 10, delay=market)
```
R=0.03: side=both seen=$128.08 sim=$-906.10 unwind=$-930.66 fees=$92.35 rebate=$2.77 wv=$1174.97
R=0.08: side=both seen=$127.65 sim=$-939.84 unwind=$-965.70 fees=$106.25 rebate=$8.50 wv=$1329.45
R=0.18: side=both seen=$126.99 sim=$-954.68 unwind=$-980.39 fees=$110.62 rebate=$19.91 wv=$1383.00
```

### 1 s (market) delay, usdc, cooldown 10, side by side
| R | seen | sim | fees | rebate | wv |
|---|---|---|---|---|---|
| 0.00 | $128.28 | $-901.34 | $90.85 | $0.00 | $1159.60 |
| 0.03 | $128.08 | $-906.10 | $92.35 | $2.77 | $1174.97 |
| 0.08 | $127.65 | $-939.84 | $106.25 | $8.50 | $1329.45 |
| 0.18 | $126.99 | $-954.68 | $110.62 | $19.91 | $1383.00 |

The rebate does not rescue the strategy: even at R=0.18 the sim is $-954.68 (worse than R=0's $-901.34, because the relaxed threshold admits more losing runs).

## Checks (all PASS)
1. **No stale 02Z/05Z runs survive:** the book-reset at gaps (35 resets, 7,443.8 s skipped) cleared the books at 02:00 and 05:00; no run opens on an unseeded leg. The 13 old runs in the first 60 s of 02Z/05Z are gone (their quotes were hour-old).
2. **Zero duplicate (event, side, t0):** 771 runs, 0 duplicates (108 removed by dedup).
3. **Zero runs opened on crossed/unseeded legs:** crossed_checks=0, unseeded_skip=0 in every sim pass.
4. **Per-run pnl sums == printed sim= totals:** verified to the cent for every side and delay in all 4 R=0 CSVs (e.g. usdc-cd10 yes delay0 csv=-302.11 == printed -302.11).
5. **At R=0, traded runs == edge_full_fee=1:** verified (the relaxed threshold adds runs to the log but not to the 0-rebate result).
6. **rebate_usd == R x fees_usd:** verified to the cent (rb03 2.77==0.03x92.35, rb08 8.50==0.08x106.25, rb18 19.91==0.18x110.62).

## Top-10 gross fraction (delay=market, cooldown 10)
### usdc
- YES: traded 19, positive 2, gross $24.40, top-10 = $24.40 (frac **1.000**). Biggest match CA Grau vs AD Tarma $12.27 = **50.3%** of gross. seen_usd top-10 $20.13 of $73.14 (0.275).
- NO: traded 32, positive 0, gross $0.00.
- Distinct positive-P&L matches: **2** (CA Grau $12.27, Deportivo Alavés $12.12).
- Top runs: CA Grau vs AD Tarma (t0 1792793824.831, dur 1.08, cost0 0.96194, q 209.0, seen 7.95, pnl 12.27); Deportivo Alavés vs Málaga (t0 1792784707.546, dur 1.82, cost0 0.93122, q 177.0, seen 12.17, pnl 12.12).

### shares
- YES: traded 126, positive 18, gross $45.84, top-10 $45.40 (frac **0.990**). Biggest CA Grau $12.27 = 26.8%. seen_usd top-10 $43.63 of $182.69 (0.239).
- NO: traded 98, positive 11, gross $3.04, top-10 $3.04 (frac 0.999). Biggest CA Juventud $1.42 = 46.7%. seen_usd top-10 $2.09 of $55.79 (0.037).

## Rebates
- Relaxed threshold (max_taker_rebate 0.5) added **376 runs** with edge_full_fee=0.
- At R=0.08: 42 of those become tradeable, seen_usd $1.47. At R=0.18: 85 become tradeable, seen_usd $5.60.
- Fees paid (R=0, market, both): $90.85. wv (buys only): $1159.60. wv_30d = $1159.60 x (720/17) = **$49,109** (17 hours covered). Tier ladder: Bronze 3% / Silver 8% / Gold 18% / Platinum 32% / Diamond 44% / Obsidian 50% (entry tier Bronze; exact dollar thresholds not in the task).
- maker_rebate_usd = 0 in all rows (every order is a taker).

## Conclusion
The clean rescan removes the fake runs (stale books at gaps, crossed books, duplicates, same-liquidity recounts). The edge does **not** survive: every sim pass is negative at every delay and unit, and taker rebates up to 18% do not change that. The old +$122 (1 s, USDC) was driven by the fake runs, exactly as the audit found.


