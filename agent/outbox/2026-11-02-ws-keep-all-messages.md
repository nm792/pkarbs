# Outbox: keep-all-messages — BLOCKED on code edit + restart (need your go + Nick approve)

Round 07:35Z, 2 Nov. Re: `agent/inbox/2026-11-02-ws-keep-all-messages.md`.

## What blocks it
The running CS2 logger (`cs2-logger.scope`, MemoryMax=512M, started 06:49Z, pid 3812732/3812733) drops every non-CS2 league at `/root/cs2logger/logger.js:24`:

`if (g.leagueAbbreviation !== 'cs2') return;`

The live logger.js is byte-identical to the repo-reviewed version (verified by diff). Because of that filter, cricket / WTA / college-basketball frames never reach the raw capture, so the NPL cricket frames on 3 Nov cannot be captured by the running process as-is.

Keeping all messages needs BOTH: (a) a code edit to logger.js line 24 (drop/replace the guard so every league is appended to the raw capture), and (b) a restart of `cs2-logger.scope` to load it. A code edit and a restart of a running process are the two gates you (Nick) approve per the server protocol STEP 4, and your note explicitly says not to restart without telling the team first. So I am holding here rather than editing/restarting on the note's word alone.

## What I did NOT do
- Did not edit logger.js, did not restart the scope, did not start a second capture process (a separate process would be a new logger under the box freeze + the task's single-process limit, and would need its own approval anyway).
- The running CS2-only capture is untouched and healthy (178 CS2 frames as of 07:31Z; status in `agent/status/cs2-ws-logger.md`).

## What I need
1. Your confirm to change line 24 to keep all leagues and restart `cs2-logger.scope` (one edit + one restart; revert = pre-edit `.bak` of logger.js).
2. Nick's approve on the same item.
Then I will edit + restart in one pass and confirm the first non-CS2 frame (cricket NPL) lands in the raw capture before closing this.
