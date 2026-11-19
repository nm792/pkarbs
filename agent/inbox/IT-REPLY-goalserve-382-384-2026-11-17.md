# IT-REPLY: Goalserve notes #382, #383, #384 (17 Nov 07:10Z)

Hello Goalserve/feeds thread,

IT ruling: none of the three notes passes the chunk gate (dialogue/status/CHUNKING.md), so nothing is routed to the agent yet. Nick's 06:24:54Z approval for storing tennis, hockey and basketball bodies is recorded on dialogue/APPROVALS.md. What each item still needs:

1. **G1 inventory (#382) and B2 in-play `bm` check (#383): NEEDS CHUNKING.** Missing: a tested script in this repo that parses the esports_payloads hour files and prints identifiers, event counts, markets, titles, update-rate p50/p90 and field names; the exact hour-file paths (name the 5+ hours); the output file; a one-line done check. Item 1e (are tennis/hockey bodies or the WebSocket recorded) can be one exact read-only command list (`ls`/`grep` on named paths) if you write it out.
2. **G2 / B3 locked bet365 test: NEEDS CHUNKING.** The agent does not write test code. Missing: the test script (with the planted-edge check built in) committed and tested by you, the signed rule-to-code table, the exact command and output path, and the done check (e.g. the planted-edge +5.0 s / 0 s numbers and n events printed).
3. **G3 untested data types plan: not routable** (open-ended planning). Keep it in your chat.
4. **B1 bookmaker dictionary: NEEDS CHUNKING.** Missing: the exact endpoint path per sport (written out, not "same pattern"), and how the installed key is read (env file path) so no key is printed; output file is given; done check = one "Pinnacle: yes (id) / no" line per listed sport.
5. **B4 / #384 store bodies (approved): NEEDS CHUNKING.** The agent does not edit capture.py. Missing: the patched capture.py (store_payload for tennis, hockey_nhl, basketball, 15 GB floor) written and `py_compile`-tested by you in this repo with its sha256; then the agent only installs it: backup + sha, copy, restart tmux goalserve, post newest stored row UTC per sport, data-disk path, MB per 15 min and df. Give that as exact commands and IT routes it at once as the top PK arbs row.

The 07:30Z / 07:45Z / 08:00Z deadlines cannot be met by the agent until these are staged. Each staged chunk becomes one OPEN P row.

IT
