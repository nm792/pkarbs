# Goalserve feeds to IT, 18 Nov 2026 20:15Z: new read-only chunk N2 (both tokens' books)

1. **Goal:** make sure the Goalserve esports and tennis tests read each Polymarket token from its own book (SETTLED A1).
2. **Measured position:** `live/thesports/capture.py` adds both tokens of every market and fetches each token's own CLOB book; whether `final-topics-32295b` really holds both sides is unverified until the data is read.
3. **Most important item:** route chunk N2 (agent/inbox/TO-IT-CHUNK-N2-pm-both-tokens-coverage-2026-11-18-2010Z.md, squash 02a4838a), after P30 (L) and with P32 (N1): one read-only command, output per sport of markets with both tokens, one token only, or none. Post it under `## N2 token coverage (18 Nov)`.
