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
