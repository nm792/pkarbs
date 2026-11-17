# Rule-to-code table (checker, 17 Nov 2026)
Rule files: FW = LOCKED-RULE-funding-window-divergence-2026-11-17.md; FU = LOCKED-RULE-divergence-followups-2026-11-17.md. Code re-read after the coordinator's change (fee_info / growth.json / cost_bp(hs, fee)). Line numbers refer to /tmp/wp6/new/*.py as of 05:17. "pl" = perplib.py, "an" = analyze.py, "f23" = follow23.py, "e1" = eval1.py, "sa" = sample_an.py.
Status key: MATCH / DEPARTS / NOT IMPLEMENTED / AMBIGUOUS. "Planted-verified" = the numbers were reproduced on synthetic data by planted_edge_check.py (independent reference loops).

## Data and definitions (FW)
| Rule text | Code | Status | Note |
|---|---|---|---|
| FW-A "every xyz, flx and km perp with at least 60 days of records" | pl:20-22 (len(F[s]) >= 1440 and oi>0) | MATCH (+AMBIGUOUS extra) | 1440 hourly records = 60 d. The extra "OI > 0" filter is not in the rule (a symbol with no OI cannot be tiered; code assumes drop). |
| FW "terciles of open interest in USD ... among the A symbols" | pl:23, pl:24-26 | AMBIGUOUS | Cut-offs c1=o[n//3], c2=o[2n//3]; thin is `<= c1`, so thin gets n//3+1 symbols (13/12/11 for n=36), not an even split. Planted-verified that code = this convention. |
| FW "B symbols labelled by the same cut-offs" | sa (no tier code) | NOT IMPLEMENTED | sample_an.py never assigns tiers to sample-B symbols; per-symbol output only. |
| FW session classes: weekend Fri 22:00-Sun 22:00; weekday-US Mon-Fri 13:00-21:00; weekday-other | pl:30-35 (sess), pl:27-29 | MATCH | Uses the hour START (t-H) of the record. Planted-verified on every tier x session cell (reference classifier written independently). |
| FW hourly record time t carries premium for the hour ending t | pl:15-19 (series), an:20, f23:20 | MATCH | Candle with open t-H is hour h. |
| FW premium in bp, fundingRate in bp | pl:18 (x1e4) | MATCH | |

## Metrics 1-3 (FW)
| Rule text | Code | Status | Note |
|---|---|---|---|
| M1 "median, 90th and 99th percentile of \|premium\| in bp" per tier x session | an:36, 39 | MATCH | Planted-verified (1e-6). |
| M1 share of hours >= 25 bp and >= 50 bp | an:40 | MATCH | |
| (all cells reported) | an:37 `if len(p) < 50: continue` | DEPARTS | A cell with < 50 hours is silently not reported; no such threshold in the rule. Harmless at real size. |
| M2 share of \|p\|>=25 hours where next hour has same sign and \|next\| >= half | an:14-16, 40 | MATCH | Planted-verified. Hours with no next record are dropped from the denominator. |
| M2 AR(1) coefficient of the premium | an:17, 38 | AMBIGUOUS | Pooled Pearson correlation of (p_t, p_t+1) pairs across symbols in the cell (not a per-symbol AR fit, no demeaning per symbol). NaN if <= 50 pairs. Planted-verified = pooled correlation. |
| M2 median run length of same-sign \|p\|>=25 hours | an:24-30, 41 | MATCH | Runs assigned to the session of their first hour; contiguity checked. |
| M3 mean \|fundingRate\| per hour in bp | an:13, 41 | MATCH | Over all hours in the cell. |
| M3 "mean funding received by the side that fades the divergence" | an:14-15 (sign(p)*FR[t]), 42 | AMBIGUOUS | Code restricts to hours with \|p\| >= 25 and uses the SAME hour's rate. Sign right: fade = -sign(p), receives sign(p)*rate. Planted-verified (+2 bp when premium positive and rate +2 bp). |
| "Material divergence" >= 5% of hours \|p\|>=25 | an:43 | MATCH | |
| "Persistent" >= 50% not reverted | an:43 | MATCH | |

## Metric 4 (FW) reversion trade
| Rule text | Code | Status | Note |
|---|---|---|---|
| "end of any hour h with \|premium_h\| >= 50 bp" | an:18 | MATCH | Every hour (overlapping allowed, as the rule says "any hour"). Requires a next record (n is not None) - not stated in rule. |
| "position AGAINST the sign of the premium" | an:22 pos = -sign(p) | MATCH | |
| entry "at the close of the 1 h trade candle of hour h", exit "close of hour h+1" | an:20, 22 (cs[t-H] close -> cs[t] close) | MATCH | Planted-verified: gross exactly 40.0 bp on a planted 40 bp reversion. |
| "funding received for hour h+1 (rate x position sign)" | an:22 f = -pos*FR[t+H] | MATCH | Rule wording "rate x position sign" is loose; code uses received = -pos*rate (long pays positive). Sign planted-verified (short receives +rate). |
| "Costs = 2 x (9 bp fee + max(3 x live half-spread, 1 bp))" | pl:5-7, pl:38-48; an:10 | DEPARTS | Fee is now per symbol: 0.9 bp if growthMode enabled (4.5 x 2 x 0.1), else 9 bp; growth map from growth.json. Rule text fixes 9 bp. 3x half-spread and 1 bp floor match. Planted-verified cost formula per symbol (3.8 bp for hs 0.2 growth; 33 bp for hs 2.5 non-growth). Departure is the coordinator's stated change; the rule file itself was not amended. |
| fee_info key lookup | pl:41-44 | AMBIGUOUS | Names with no ":" are assumed dex "xyz"; growth map is looked up by full symbol then bare name. "checked" True only for xyz growth symbols. |
| "live half-spreads from l2Book at analysis time" | pl:46-48, an:19 | AMBIGUOUS | A symbol with no half-spread is excluded from metric 4 (rule silent). |
| "Reported per tier x session class" | an:34-51 | MATCH | Session of entry hour h. |
| "weekend-cluster bootstrap 95% CI (calendar-week clusters, 10,000 resamples, seed 1)" | pl:49-55, pl:5; an:47 | MATCH (read only) | ISO calendar-week clusters of the event end time; pooled-mean ratio-of-sums resampling; default_rng(1); 10,000; 2.5/97.5 pct. The CI numbers were not independently recomputed; only that CIs bracket the planted mean and tradable flags are right. |
| "Tradable reversion": mean net > 0, CI lower > 0, n >= 30 events, >= 8 calendar weeks | an:48 | MATCH | Planted-verified True when 14-week planted edge; False in no-edge and funding-only (negative) cases. |
| "Anything else is reported as no tradable reversion" | an:48-51 | AMBIGUOUS | Prints tradable=False rather than the phrase; no wording issue in substance. |
| M4 "(single, mechanical)" overlapping trades | an:18-23 | AMBIGUOUS | Consecutive qualifying hours each produce a trade (overlap in the held hour); weekly clustering is the only correction. |

## Metric 5 (FW) sample B
| Rule text | Code | Status | Note |
|---|---|---|---|
| per symbol and per hour-window max \|mid - oracle\|, max \|mark - oracle\| in bp | sa:8, 13, 19 | MATCH | Hour window = UTC hour of the sample timestamp (key int(t//3600)). Planted-verified (30.0 / 4.0). |
| time for \|mid-oracle\| to fall below 5 bp after it exceeded 25 bp | sa:15-18 | AMBIGUOUS | Uses only the FIRST >=25 sample in the window; seconds = first later sample < 5 bp minus that time (5 s granularity). Planted-verified 60 s. |
| share of exceedances that revert before the next top of the hour | sa:22-23 | AMBIGUOUS | "Revert" = reverts within the same hour window; windows cut by the 30 min sample may be partial. |
| Polymarket index in place of oracle | sa:12 (field "oracle") | AMBIGUOUS | Works only because the sampler writes the PM index_price into "oracle" (sampler.py line 16). Not verified against real PM rows beyond that. |
| 30 minute / descriptive only | sa | MATCH | Nothing inferential is computed. |

## Follow-up common cost model (FU)
| Rule text | Code | Status | Note |
|---|---|---|---|
| "taker fee 9 bp per side on Hyperliquid builder dexes" | pl:38-44 | DEPARTS | Same as above: 0.9 bp for growth-mode xyz assets; 9 bp otherwise (flagged COST UNCHECKED in outputs, an:51, f23:37, f23:80). |
| "Polymarket ... 4 bp per side" | e1:6 FEE = 4.0 | MATCH | Planted-verified net = gross - 8. |
| "live l2Book half-spreads stressed 3x with a 1 bp floor (tests 2, 3)" | pl:46-48 | MATCH | |
| "Bootstrap = weekly-cluster for history, event-cluster for the live tests, 10,000 resamples, seed 1" | pl:49-55; e1:93-95 | MATCH / AMBIGUOUS | History: weekly. Live: cluster = symbol x (date, session class) (e1:93); "event-cluster" is not defined in the rule, this is the code's assumption. Seed via default_rng(1), 10,000. |

## Test 1 (FU) eval1.py
| Rule text | Code | Status | Note |
|---|---|---|---|
| "evaluation uses only the sessions recorded after this rule is merged" | e1:8 (glob of all files in LOGDIR) | NOT IMPLEMENTED | No date/merge-time filter; the caller must pass only post-merge files. |
| Gap g = (mid - index)/index in bp | e1:38-40 | MATCH | |
| "Signal at the first 5 s sample with \|g\| >= 25 bp for a symbol with no open trade" | e1:78-80, 86 (i = j+2) | MATCH | No open trade = skip to after the exit-fill sample. |
| "Position = against g" | e1:81 | MATCH | |
| "Entry at the NEXT 5 s sample, only if \|g\| is still >= 15 bp" | e1:82, 64 | MATCH | Sign of g is not re-checked, only magnitude. Missed counted (e1:82, 88); planted-verified 90 of 90. |
| "fill = VWAP of $1,000 notional walked through that sample's book on the far side" | e1:41-49, 64 | MATCH | Planted-verified with a 2-level book. Assumes levels are listed best-first (not sorted or checked). Insufficient depth -> trade dropped and counted as "no usable book". |
| "Exit: first sample with \|g\| < 5 bp, or 300 s after entry" | e1:67-68 | MATCH | 300 s measured from the entry sample time; planted-verified hold 305 s (trigger sample then fill at next sample). |
| "fill at the book of the sample after that trigger" | e1:69-71 | MATCH | |
| "Gross = position x (exit/entry - 1)" | e1:85 | MATCH | |
| "Net = gross - 2 x 4 bp - funding paid if a top-of-hour settlement is crossed (rate from /v1/info/funding)" | e1:51-61, 85-86 | MATCH | Boundary strictly after entry-sample time and <= exit-fill time; position paid = pos*rate (positive rate, long pays). Planted-verified both signs (short receives, long pays) with a 30 bp rate. An entry exactly on the boundary is not charged (strict <), which is a convention. Missing rates counted and treated as 0 (reported). |
| funding rate units | e1:59 (rate*1e4) | AMBIGUOUS | Assumes funding_rate is a fraction per settlement interval. Not verifiable offline. |
| Placebo "same symbol during the same session with \|g\| < 10 bp, random direction, same exit rule, same costs (seed 1)" | e1:97-104, e1:6 | MATCH / AMBIGUOUS | Same symbol and same session verified on planted data (placebo mean -13.2 vs -12 expected; wrong symbol/session would give about -50). "Session" = (UTC date, class) pair; one placebo per event, trades may overlap. |
| "PASS only if >= 30 events over >= 2 calendar days AND mean net > 0 AND CI lower > 0 AND mean net > placebo mean" | e1:111 | MATCH | days = UTC dates of signal time. |
| "Fewer events or one day labelled PRELIMINARY and the number of events and days needed is stated" | e1:111-112 | MATCH | Label is "PRELIMINARY / NOT PASS" (it is also printed when events are enough but the means fail; wording only). |

## Test 2 (FU) follow23.py carry
| Rule text | Code | Status | Note |
|---|---|---|---|
| "hist.json and cand.json ... 108 perps on xyz, flx, km" | f23:6 | AMBIGUOUS | Universe = >= 1440 records and candles present and (OI>0, or dex flx/km even with OI 0). xyz with OI 0 is dropped but flx/km with OI 0 are kept as "thin": inconsistent treatment. |
| "Event: end of an hour with \|premium\| >= 50 bp. Position against the premium sign, entered at that hour's closing candle price, held k = 6 hours, exit at close of hour +6" | f23:19-22 | MATCH | Planted-verified gross exactly 40.0 bp for k = 3, 6, 12. |
| "funding received over the 6 settlements (funding = position x -rate; on flx the rate is as recorded)" | f23:23 | MATCH | Records t+H..t+kH. Missing records are silently counted as 0 funding (f23:23). Planted-verified: +/-12 bp for k=6 at 2 bp rate, +/-6 (k=3), +/-24 (k=12). |
| "Net = ... - 2 x (9 bp + max(3 x live half-spread, 1 bp))" | f23:11, 25 | DEPARTS | Per-symbol fee as above (0.9 growth / 9). |
| "Sensitivity reported only: k = 3 and 12" | f23:38 | MATCH | Labelled sensitivity only; they still print a PASS= flag (cosmetic). |
| "non-overlapping (no earlier event of the same symbol still open)" | f23:17, 19, 25 | MATCH | free = t + kH; an event exactly at exit time is allowed (convention). Planted-verified n against reference. Events skipped for missing candles do not block. |
| Subset (a) dex xyz vs flx+km | f23:7, 31 | MATCH | |
| Subset (b) OI tercile | f23:31 | MATCH | Same cut-offs. |
| Subset (c) "persistent events where \|premium\| >= 100 bp of the same sign for 3 consecutive hours before entry" | f23:24, 32 | AMBIGUOUS | Window = hours h, h-1, h-2 (the entry hour plus the two before). Alternative reading h-1..h-3 is not used. Also (c) is a subset of the primary non-overlapping stream rather than a fresh non-overlapping stream. Persistent x tier cross not reported. |
| "PASS ... n >= 30 non-overlapping events over >= 8 calendar weeks AND net mean > 0 with 95% CI lower bound > 0. Else no tradable carry" | f23:37 | MATCH | |
| (cells reported) | f23:35 `if len(v) < 10: continue` | DEPARTS | Cells with < 10 events are not printed at all; no such rule. |
| output formatting | f23:37 | cosmetic | `{key[0]:10s}` is 10 wide so "persistent" prints glued to "all" ("persistentall"). |
| robustness | f23:96-101 | DEPARTS (defect) | If there are no Test 3 episodes (no 3-hour >=100 bp run) the logistic block crashes with IndexError at `Xtr.shape[1]` after all Test 2/3 output has printed. Reproduced on every planted dataset without episodes (C1, C2, C3). Real data with BIRD-like runs will not hit it, but it is a crash on well-formed input. |

## Test 3 (FU) follow23.py frozen oracles
| Rule text | Code | Status | Note |
|---|---|---|---|
| "Episode: a maximal run of >= 3 consecutive hourly premiums with the same sign and \|premium\| >= 100 bp" | f23:44-49 | MATCH | Planted-verified episode count 792/792. |
| "Reset = the first hour afterwards with \|premium\| < 25 bp" | f23:51-54 | MATCH | Searched over contiguous records; a data gap or data end leaves it censored (reported as "censored/never"). |
| (a) "distribution of run length and of \|premium\| before the reset, by dex and tier" | f23:60-63 | AMBIGUOUS | Prints median and p90 of run length and only the MEDIAN \|premium\| of the last run hour, not a distribution; \|premium\| "before the reset" is taken as the last run-hour premium. |
| (b) hazard P(reset in next hour \| run length n), n = 3..12 | f23:65-68 | AMBIGUOUS | At risk = episodes with run >= n; reset counted only if the run ends at n AND the very next hour is < 25 bp. Stops printing when < 10 at risk (undeclared threshold -> DEPARTS for n beyond that). Planted-verified table. |
| (c) "the perp's own 1 h candle return in the reset hour, signed toward the oracle (x -sign(premium)), versus the premium before the reset: mean, median, regression slope" | f23:70-74, 83 | AMBIGUOUS | Return = candle of the reset hour, x -sign. Regressor = \|premium\| of the LAST RUN hour (f23:74 abs(e["p"])), which for episodes whose reset is not the very next hour is not the premium immediately before the reset. Planted case: code slope 0.5, literal "premium before reset" reading gives about 0.16. |
| (d) "logistic regression of reset in the next hour on run length, \|premium\| and an hour-of-day/weekend indicator, with out-of-sample AUC on the last 30% of weeks" | f23:89-106 | DEPARTS (partial) | Only a weekend indicator; no hour-of-day term. Train/test split = first 70% / last 30% of calendar weeks present. Ridge 1e-3 added. Runs and prints AUC (planted: ran). |
| Ex-post bound: "enter against the premium at the close of the third hour of the episode, exit at the close of the reset hour, same costs" | f23:75-79, 84 | MATCH | Planted-verified gross = 0.5 x mean \|p\| exactly, funding 0, net = gross - per-symbol cost. Funding over settlements t3+H .. reset hour; missing = 0. Costs per-symbol (same fee DEPARTS). |
| "If even this ex-post bound is not net positive, no tradable jump" | f23:84 | AMBIGUOUS | Prints the numbers, no verdict string. |
| "What the venue settles against ... reported as not verified from docs" | none | NOT IMPLEMENTED | A reporting statement, not code; must be in the write-up. |
