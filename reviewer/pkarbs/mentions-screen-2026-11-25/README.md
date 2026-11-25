# Will-say / mentions family: volume, depth, first screen (Reviewer, 25 Nov 2026 01:55Z)

Nick 01:41Z: the "says" contracts trade millions a month and have been neglected. This is the top PK priority, alongside the trial-feed timing. Paper only; nothing traded.

## 1. Volume (gamma tag `mention-markets`, events closed since 26 Oct; vol.py)
| Family | Events (30 d) | Volume | Share |
|---|---|---|---|
| Trump (rallies, meetings, monthly word lists) | 25 | $1,121,071 | 81% |
| Other (Fed/Warsh, CEO keynotes, interviews) | 18 | $137,956 | 10% |
| Earnings calls | 20 | $113,225 | 8% |
| Creators / streams | 4 | $18,336 | 1% |
| **Total** | **67** | **$1,390,588** | |
The largest events were Trump's Lubbock rally ($329,853), the Xi/Putin trilateral ($163,899), "foods Trump mentions in October" ($150,504) and the Thanksgiving pardon ($59,514). Volume comes in bursts around the speech itself.
**Open now (9 events, ev.py):** Jensen Huang GTC DC ($22.6K so far, ends 2 Dec), Trump APEC China ($19.5K), Trump November ($10.3K), Trump Philippines, Salesforce call ($4.4K, ends 3 Dec), Deere call (25 Nov), plus stale announcer and Caedrel events.

## 2. Forward test of the frozen 10c base-rate rule (scorer run in the cloud, 25 Nov; forward_LATEST.txt)
Since the 10 Nov freeze: 19 forward events, 13 resolved, **6 resolved bets: 1 win, -$26.51 after fees**, plus 3 pending. Paired t vs placebo -1.19. Each bet is sized to one recorded print, so this is not a depth result. 0 bets were filled from a recorded own-token book: the P121 books were never scored (IT P147 filed).

## 3. Screen: open events, each token's OWN asks vs the causal per-word base rate (screen.py, screen_open.json)
106 tokens checked. **11 have asks at least 10c under the base rate, worth $1,375 in total at those asks.** The biggest is Jensen Huang "AI (30+ times)" YES: best ask 0.57, fair 0.877, $493 at edge.
**Defects in this screen (do not trade off it):**
- (a) The frozen rule strips digits, so "AI (30+ times)" pools with plain "AI" history and the fair is inflated. This is OPEN-ITEMS 25; the flag exists in the scorer (KEEP_THRESHOLD) but is off by default.
- (b) The Jensen Huang words fall in the generic "other" family, so "Affair / Spy" and "Stock Market / 401K" carry Trump-style base rates.
- (c) It is a snapshot at 01:50Z, not at a decision time.
So the $1,375 is an upper bound, and most of it sits on mispriced fairs.

## 4. Edges to test, per the whole-family rule
| Edge | Where the money is | State | Next step |
|---|---|---|---|
| A. Base rate vs own ask (frozen 10c) | Listing-time books; edge-priced depth is about 1% of each ladder | Forward: 6 bets, -$26.51; screen: $1,375 upper bound with defects (a, b) | Rerun with KEEP_THRESHOLD on and a transcript base rate per speaker (L3), by 10:00Z |
| B. Live speech nowcast (transcript or captions, hazard model) | The event itself, which is where the 81% Trump volume trades | Design only (9138be8025) | Spec with caption source and 250 ms bar, planted case (L4), by 26 Nov 06:00Z; replay on the next Trump speech |
| C. Maker quoting on word markets | Spreads of 40-97c on calls (Dell read) | Untested | Measure fill and markout from recorded P121 books plus /v2/trades prints, after P147 |

## 5. Rerun with the count-word fix (KEEP_THRESHOLD on; screen_kt.py, 02:25Z)
14 tokens have edge-priced asks, worth $2,634 in total. The count words flip as expected: Jensen "AI (30+ times)" is now a NO (fair 0.595), where the frozen rule said YES. The new top row is Salesforce "Data Center" YES at $1,043, but its fair of 0.915 comes from OTHER companies' calls, since history is pooled across the earnings-call family. That fails the speaker test. **Next (L3, due 10:00Z):** per-speaker transcript base rates for Salesforce (last 4 calls) and for Jensen Huang's last keynotes. Then rescreen only the words with speaker-level history.
