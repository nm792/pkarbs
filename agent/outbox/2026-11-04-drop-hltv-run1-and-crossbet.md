# outbox — 2026-11-04-drop-hltv-run1-and-crossbet

Status: executed per reviewer's 13:18Z note.

- **HLTV scorebot run 1: stopped + cleaned up.** It WAS running on the server (two duplicate `node capture.js config-run1.json` processes, started 12:18:35Z and 12:19:43Z; pids 637770/638865 + timeout parents 637765/638862). Killed both; `ps`/cmdline scan confirms no `capture.js config-run1` process remains. `free -m` before: used 4014 MB / free 353 MB; after: used 3533 MB / free 834 MB (~481 MB freed, matching the 2×400 MB caps). Run 2 (IEM playoffs 6 Nov) NOT started — waiting for the new approval note.
- **cross.bet reachability: dropped.** Not run (low value, per note). No cross.bet process or artifact created.

## Note / not deleted
- `/root/hltvcap/run1-2026-11-04/` holds ~647 MB of captured files (scorebot.jsonl 643 MB, books.jsonl 19 MB) written 12:18Z→13:36Z before the stop. Left in place (removing data is destructive and not asked); say the word and I delete it. The 12:18Z/12:19Z double-start was two launch attempts of the same job both landing — a single hermes job firing twice, not two distinct tasks.
