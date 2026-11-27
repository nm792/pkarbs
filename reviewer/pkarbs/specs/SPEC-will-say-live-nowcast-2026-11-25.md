# SPEC v1 (pre-registered, locked 25 Nov 2026 16:20Z): "will X say Y" LIVE NOWCAST: measure the reprice window after a word is spoken (OPEN-ITEMS 24, ledger will-say)

Reviewer. Measurement first, no trading, no new data feed (Nick 25 Nov: no new feeds until PandaScore and Goalserve are timed). Runs on Prime (R-039). Known facts: SETTLED A1 (own-token books only), A3 (250 ms taker hold on non-weather markets), B1 (resolution finer than the delay tested, planted case), INSIGHTS I-10..I-18. MC types named per G64.

## Question
When a speaker says a listed word during a live event, how long does that market's YES token keep an ask below (1 - fee - 2c), and how much $ sits at those asks? If the window is longer than our achievable latency (speech-to-order) plus the 250 ms hold, a live nowcast has room; if it closes in under ~1 s, it does not, whatever the word model.

## Data (already recorded or public)
- Books: P121 WS paper logger records own-token books for every mention-markets token in scope (since 23 Nov 12:57Z; ms receive time on Prime's clock). Earnings-beat and will-say events covered.
- Word times: the event's public replay (company IR webcast / YouTube / C-SPAN) with a timestamped transcript. Utterance time t_w = replay timestamp + the stream start time, both written down with their source. Stated resolution: +-1 s (transcript word timing) unless a word-level aligned transcript exists; the result is labelled with that resolution.
- Events: every mention event P121 recorded that resolved YES on at least one word since 23 Nov (Dell 24 Nov call, Deere 25 Nov call, Thanksgiving pardon 24 Nov, Trump remarks, others in decisions.jsonl). Listed with counts before any book is read.

## Measure (per word that resolved YES)
- Ask path: own YES best ask and depth at <= (1 - fee - 0.02) from t_w - 60 s to t_w + 300 s.
- Window W = first time after t_w at which no ask <= (1 - fee - 0.02) remains, minus t_w. W < 0 means the market moved before the word (leak or anticipation); recorded, not dropped.
- $ available = sum of price x size at those asks at t_w + L for L in {1, 2, 5, 10, 30} s (our latency cells), each net of the 250 ms hold (book at t_w + L + 0.25 s).
- Placebo (MC type 1, random times on the same data): 10 random word-free times per event, same windows; report W and $ next to it.
- Planted case (MC type 2, randomised data, power): in a copy of the books, keep a stale ask of 0.50 x 100 shares on 50% of the YES words for exactly 3 s after t_w; the scorer must report W within 2.75-3.25 s and $ at L=1 s of about $50 on those words, and unchanged values elsewhere. A run whose plant fails is void. A second plant with the stale ask removed at t_w + 0.25 s must show $ = 0 at L >= 1 s (checks the 250 ms hold handling).

## Verdict (per sub-family: earnings calls, Trump, keynotes, other; no pooling across them)
- ROOM if the median W >= 5 s and the median $ at L = 2 s >= $50 per word, with n >= 20 YES words in that sub-family, both above the placebo's 95th percentile.
- NO ROOM if the median W < 1 s with n >= 20.
- Else INCONCLUSIVE, with n and the date by which P121 will have 20 words.
ROOM does not mean a strategy: it only says a speech-to-order system could be worth building, and that build would need Nick (new feed + server code).

## Delivery
Scorer + tests (both plants, placebo) 26 Nov 12:00Z under reviewer/pkarbs/will-say-nowcast/; event list and word timestamps from public replays by the same time (the external agent can pull transcripts via a webb task); IT run on Prime after that.

## Amendment v1.1 (25 Nov 18:40Z, before any data was read)
Reason: the v1 data source does not exist. it/mentions_pm_ws_paper.py (P121) keeps no continuous book log for will-say tokens: it writes decision rows at its slots, plus earnings-beat books once every 60 s. A 60 s snapshot cannot measure a window of seconds (SETTLED B1).
- Data: public taker trade prints of each YES token (Data API v2 /trades, default takerOnly=true, integer-second timestamps). A taker BUY walks from the best ask, so:
  - W_ub is the first BUY print above the cheap threshold after t_w. No cheap ask remained at that point.
  - W_lb is the last cheap BUY print before W_ub. Cheap asks existed at least until then.
  - W is bracketed as [W_lb, W_ub]. W_ub < 0 means a leak.
- $ at L counts cheap BUY prints at or after t_w + L + 0.25 s, up to t_w + 300 s. It is a FLOOR: asks nobody lifted cannot be seen, and we would compete for these.
- Resolution is 1 s on prints plus +-1 s on the transcript. L = 1 s is BELOW RESOLUTION and L = 2 s is AT RESOLUTION. Neither enters the verdict.
- Verdict, per sub-family (no pooling):
  - ROOM: n >= 20, median W_lb >= 5 s, and median $ at L = 5 s >= $50 and above the placebo 95th percentile.
  - NO ROOM: n >= 20 and median W_ub < 2 s.
  - Otherwise INCONCLUSIVE.
- Placebo (MC type 1): 10 random pre-word times per word in [t_w - 6 h, t_w - 300 s].
- Plants (MC type 2): a 100 sh @ 0.50 stale ask lifted at t_w + 3.0 s, which must give W_lb in 2.75-3.25 s and exactly +$50 at L = 1 and 2 s, with nothing else changed. A second plant lifted at t_w + 0.25 s must give $0 at every L >= 1. If either plant fails, the run is void.
- Word times: webb T112, 32 resolved-YES words in 8 events since 15 Jul. It is in PR #203 and needs Nick's merge.
- Expected outcome on n:
  - The current sub-families have earnings 9, Trump 9 and other 14 YES words. All will be INCONCLUSIVE on n alone until more events resolve.
  - These 8 events traded $2K-$60K each in total, so $50 per word at L = 5 s is a high bar.
