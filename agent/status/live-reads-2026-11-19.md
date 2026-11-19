## P78 live reads (19 Nov 2026)

Read-only run of the reviewer-provided P78 block; no restart, edit, or stop. Sample window 15:48:04–15:53:50 UTC; follow-up process checks through 15:55 UTC.

| Item | Result | Evidence |
|---|---|---|
| PandaScore RAW capture | PASS | P71 capture PID 3323067 remained alive (elapsed 04:34 at 15:54 UTC). `pandascore_2026111915.jsonl.gz` grew from 428,028 B at 15:48:04 to 483,119 B at 15:53:49 (+55,091 B); file timestamp 15:53:49 UTC. |
| PandaScore CS2 probe | PASS, with errors | `cs2probe` tmux session and loop PID 3273611 were live; worker PID 3578563 was live. Output log grew to 160,497 B at 15:53:48; newest event summary was `15:52:45Z events: 34`. The log also contains repeated WebSocket `4004 Match is unavailable` errors, and earlier loop iterations through 14:21Z failed preflight (`every_pm_token_has_a_book_message`); not a clean run. |
| PM CS2 books | PASS | PID 3179608 remained alive. `books.jsonl` grew from 1,030,233,946 B at 15:48:04 to 1,031,789,264 B at 15:53:50 (+1,555,318 B). |
| PM Dota books | PASS | `check_pmdota.sh` at the reviewer-specified revision returned PASS; PID 2539785 remained alive. `books.jsonl` grew from 4,795,868 B at 15:48:04 to 5,328,338 B at 15:53:50 (+532,470 B); newest row age was 1 second in the check. |
| Goalserve, esports / tennis / NHL / basketball | PASS | Capture PID 4045212 was live. Current-hour files grew respectively from 8,580,294 / 111,407,441 / 13,908,856 / 10,538,058 B at 15:48:04 to 9,575,688 / 126,789,205 / 15,582,671 / 11,620,300 B at 15:53:50 UTC. |
| AAA watcher | FAIL / no rows | No watcher process found. `aaa_watch.jsonl` was 0 B, mtime 07:28 UTC; no status counts or first/last row timestamps exist. |

Free space at 15:49:06 UTC: VOL2 35,875,664,992 B; repo volume 4,978,282,496 B. Follow-up at 15:53:50 UTC: VOL2 35,185,876,992 B; repo volume 4,930,486,272 B.

The supplied P78 script itself exits 1 at the AAA counts step because the JSONL has no rows (`IndexError: list index out of range`); the counts printed before the error were empty. No further action was taken on the watcher or any other process.
