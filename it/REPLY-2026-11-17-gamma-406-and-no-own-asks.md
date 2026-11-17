# Reply to IT: two questions on the shadow logger, and PR #394 (17 Nov 2026 09:45Z)

1. **Goal:** find and build automated Polymarket edges worth $500/day with no catastrophic loss.
2. **Where we stand (measured):** no validated edge. The sports MECE NO side is untested because no NO-token book was ever recorded. PR #393 (merged, 6b7cd07bd4) records both tokens; PR #394 (a159f6b55a) prices NO legs from the NO token's own asks in the detector and sim. Tested offline only (6 plus 3 checks in `shadow/test_no_subscription.py`, 25 of 25 in `shadow/test_gates.py`); nothing has run on the box.
3. **The one item that matters most:** has the box shadow logger been capturing at all? On 17 Nov ~09:30Z gamma answered `/events/keyset?limit=100` with HTTP 406 `{"error":"gzip_required","hint":"send the header Accept-Encoding: gzip. /events and /events/keyset pages with limit above 50 are served compressed only."}`. The logger code before #393 sent no such header and printed "gamma error ... 406", then found zero events. If the box runs that older code, it has captured nothing since gamma started requiring this.

**Questions for IT (please answer in it/):**
- When did the box shadow logger last write a non-empty `raw-*.jsonl.gz` or `events.jsonl`, and what does its log show for `gamma error`? That date is when the 406 started to bite, if it did.
- Which commit does the box run? #393 fixes it (adds `Accept-Encoding: gzip` and decompresses).

**What to deploy:** `claude/project-thread-vg2ckg` at or after the #394 merge. Same command as before, output to the mounted volume, root-disk floor respected (your note of 09:3x on the disk). Old runs with a "no" side are skipped by the sim and counted ("skipped N legacy NO runs"); new runs carry `own_book: true`.

Confidence 8/10 that the 406 is real (reproduced from this session, with the response body above); unknown whether it hit the box.
