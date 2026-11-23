# Mentions: designs for (23) transcript base rate and (24) live speech nowcast, and (26) earnings-beat plan
Order R-064 (Nick 23 Nov 08:33Z). Designs only: nothing here has been run. Every statement about data not yet seen is labelled UNTESTED. Paper only.

## 23. Transcript base rate (new words, per event type and length)
**Question.** For a market "Will X say W (k+ times) during E?", what is P(count >= k) before the event, when W has little or no earlier market history? The frozen rule uses q = (wins + 2*family prior)/(n + 2) from earlier Polymarket resolutions. That is blind to words with no market history and to the event's length.

**Model (per event type, per word).** Count of W in an event of length L minutes ~ Negative Binomial with mean mu = r_W * L and dispersion phi (speech counts are over-dispersed; Poisson is the baseline to beat, not the choice). P(count >= k) = 1 - NB CDF(k-1). r_W is the word's rate per minute in past transcripts of the SAME speaker type (earnings calls by company, Trump rallies, Trump news conferences, booth broadcasts).
- Estimate r_W with shrinkage: r_W = (c_W + a*r_family) / (T + a), c_W = word occurrences in past transcripts, T = minutes of transcript, r_family = pooled rate for the speaker type, a = prior minutes (start 60, tune on training half only).
- Match tokens the way the market resolves: "Agent / Agentic" = either form; plural and possessive rules read from each market's rules text. Count markets need the threshold k in the key (see R-064 2a: the frozen scorer pooled thresholds; fixed behind KEEP_THRESHOLD).

**Data (where it comes from).** Earnings calls: transcripts of the company's previous 8 calls (public IR pages or a transcript vendor; availability and licence UNVERIFIED, first task is to count how many of the 126 earnings-call events since 1 Jan have 4+ prior transcripts reachable). Trump: public speech transcripts (White House, Rev, Roll Call Factba.se type archives; reachability UNVERIFIED). Booth broadcasts: no public transcripts (UNTESTED; likely out).

**Test (pre-registered before any run).**
1. Freeze: model class, a = 60, 8 prior events, 10c edge, first-hour first BUY print entry, same fee and 5c-95c band as the frozen rule. One change vs frozen: q comes from the transcript model.
2. Time split: fit on events before the median date, score the later half; second pass with the halves swapped.
3. Benchmarks, in this order: (i) frozen market-history q; (ii) the market price itself (log score); (iii) a placebo: shuffle word labels within the same event.
4. Pass bar: out-of-sample log score better than the market price on events where the frozen rule has no history (new words) AND positive net at the 10c rule with paired t >= 2 on the later half. Estimate-and-shrink reporting, no hard kill on one threshold (MODELLING-PRINCIPLES 5).
5. Capacity: price each token from its OWN book at decision time at $200/trade, $2,000/day cap (R-034). Until the WS logger (P-MEN-1800 / pre-flight 227e4ef9) has run, any $/day is FLOOR.
**What would settle it.** 4+ prior transcripts for at least 60 of the 126 earnings-call events and a positive later-half log-score gain on new words. **Stack layer?** Yes: it feeds the same rule with better q; small gains stack. **Stand-alone $/day:** none claimed; earnings calls are 7.5% of 30-day volume (DISCARDED-AUDIT C), so the ceiling is small unless Trump transcripts work.
**Build cost.** 2-3 days offline: transcript fetch, tokenizer matching market wording, NB fit, scorer variant. Needs no server code (R-047).

## 24. Live speech nowcast (hazard model on a live transcript or captions)
**Question.** During the event, P(W reaches k mentions by the end | count so far, time elapsed, time left). Volume is at event time ($279K in the 24 h before end; P-MEN-1600), and the frozen listing fair loses during the event (-$78.93/day, z -2.34), so only a model that updates on what has been said can use it.

**Model.** State (c, t): count so far, minutes elapsed; L = scheduled or projected length. Remaining count ~ NB with mean r_W * (L - t) where r_W is the speaker-type rate from (23), updated by the within-event rate: r_eff = (c + a*r_W)/(t + a) (Gamma-Poisson update). P(YES) = P(c + remaining >= k). YES snaps to 1 the instant c >= k and a "said" market (k = 1) snaps at the first mention. For event length uncertainty (Q&A runs over), use a length distribution from past events of the type.
**Inputs needed.** A live caption or transcript stream with latency below the venue's 250 ms hold (SETTLED A3) is impossible for most feeds (broadcast captions lag seconds). So the viable use is NOT racing the snap; it is pricing slow drift: the market is slow to decay a "not yet said" word as time runs out, and slow to lift a word whose count is near k. Latency bar therefore: caption lag under about 5 s is enough for the drift version, UNTESTED. The snap version (race) needs under 250 ms: not feasible, label it out.
**Data.** (a) Caption or ASR transcript with timestamps for past events, to fit the hazard and measure how far the market lags; the WS logger's own-token book snapshots supply the price path once it has run on Prime (none recorded so far, so this is UNTESTED end to end). (b) Gamma/CLOB prints exist for past events, books do not.
**Test (pre-registered).**
1. Replay: for each past event with a timestamped transcript and trade prints, compute the nowcast P at every print; entry when |nowcast - print price| >= 10c (same cell as the frozen rule), hold to resolution, taker fee, own-token ask depth where recorded else FLOOR.
2. Benchmarks: market price; frozen listing fair (known -$78.93/day); a nowcast with shuffled word counts (placebo, same event).
3. Lag control: delay the transcript by 0, 2, 5, 10 s and report the edge at each; the edge must survive 5 s or it is not capturable from a caption feed.
4. Split: fit r_W on the first half, score the second; paired t and log score; no verdict below 100 event-bets.
**What would settle it.** Whether the market lags the nowcast by more than 10c at 5 s caption delay on a sample of 100+ events. **Stack layer?** Yes if positive; capacity is the large-volume segment, so this is the only mentions idea with room above $100/day. UNTESTED, confidence in any positive result 3/10 until the replay runs.
**Build cost.** 4-5 days, dependent on transcript timestamps for past events (UNVERIFIED availability) and on the WS logger collecting books.

## 26. Earnings-beat follow-up plan (dates)
**State.** The earlier "+6.8c +- 3.2c (train +1.4c)" test was lumped with Netflix and MrBeast and never followed with own-token books (REAUDIT row 27). Live gamma read 23 Nov 09:20Z (tag earnings): open "beat quarterly earnings" listings include Dick's Sporting Goods (volume $13.2K, ends 23 Nov), Analog Devices (ends 24 Nov), Dell (24 Nov), Marvell (1 Dec); older listings (Confluent, EA, Grab, Theravance) show end dates in the past and are still not closed.

| date (Z) | step |
|---|---|
| 23 Nov 14:00 | List every closed and open beat-quarterly listing since 1 Jan with volume, end date and resolution; locate the file that produced the +6.8c figure (not in pkarbs; the Reviewer to point, or I rebuild it) |
| 24 Nov 12:00 | Add the beat tag to the WS paper logger universe as a second tag (needs IT only for the same deploy row as P-MEN-1800; no extra server code) so Dell and Analog Devices books at decision time are recorded |
| 26 Nov 12:00 | Offline rescore of the beat contracts with the v2 placebo (same side, price within 5c, other events), time split, at the 10c rule on print data: estimate and CI, labelled FLOOR |
| 1 Dec | Marvell (1 Dec) is the first event with a full own-token book path; report MEASURED depth at $200 if the logger ran |
**Stand-alone:** unknown; volume per listing is $2K-13K, so stand-alone is small. **Stack layer:** yes, if the train/test sign agrees.

Confidence 7/10 on the designs as designs (nothing run); 3/10 that either (23) or (24) passes. To raise: count the available transcripts (23) and a caption-lag sample (24).
