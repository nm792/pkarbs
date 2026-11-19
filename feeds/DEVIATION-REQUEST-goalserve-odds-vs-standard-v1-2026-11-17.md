# Deviation request to Nick: Goalserve odds test vs STANDARD v1 and a change to the planted-edge gate. 17 Nov 2026

The independent checker (Audit CS2 model thread) accepts the technical case but says Nick must approve before any run. Nothing has been run on real data.

**Deviations from STANDARD v1 (all STRICTER, so no extra false-pass risk):**
1. Bar 4 (price moves after the feed) counts ALL events, with lead at least one book-snapshot gap (1 s, or the measured p90 gap if larger). STANDARD v1 counts events with an onset and lead above zero.
2. A cell needs at least 30 placebo onsets in at least 30 matches, else the verdict is 'unknown (placebo too thin)'. STANDARD v1 has no such gate.
3. The placebo excludes +-120 s around events, not +-60 s, because price reactions to events 60-120 s away otherwise contaminate it (a planted 15 s lead read as 27 s).

**Change to the pre-registered planted-edge gate (a weakening, not a strengthening):** the pre-registration said a 5 s shift on the REAL Polymarket series must pass the bar before the run. On synthetic noisy series a 5 s lead is recovered but cannot pass the bar at about 120 events (planted 25 s passes 15 of 20 seeds, planted 15 s passes 10 of 20). The real-series 5, 15 and 25 s planted run is therefore done AFTER the first real run and its result is attached to the same report. The risk is false negatives: a real lead of 2 to 10 s would read 'no lead' or 'unknown', not 'pass'. False passes were 0 of 20 (author) and 0 of 40 (checker) at lead 0 and at no edge.

**Nick: approve? Reply yes to approve the three stricter rules and the amended planted-edge gate. Reply no to keep the pre-registered 5 s real-series gate (then the first run waits for the real PM series to be shifted and re-run first).**
