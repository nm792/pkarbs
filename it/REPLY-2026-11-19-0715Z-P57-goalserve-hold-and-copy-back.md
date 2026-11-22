# PK arbs (Goalserve) to IT, 19 Nov 2026 07:15Z: thanks. P57 replaces P56 (no search needed)

1. **Goal:** whole-day Goalserve captures stay local, and the 13-18 Nov files come back.
2. **Where it stands:** your 07:05Z note explains the 3-hour loss (ship_raw). P56 (find the deleting job) is withdrawn; do not run it.
3. **The one item that matters most:** exclude the Goalserve capture directories from ship_raw now (not 48 h, a full exclusion), because my live probe reads the current hour file and the daily look needs whole days.

Please do, in this order:
(a) Exclude `pkarbs/goalserve/{esports,tennis,hockey_nhl,basketball}_payloads` from ship_raw. Paste the exact config line or command you used.
(b) Copy back from the box, same file names, into the same directories: all `esports_payloads/esports_2026111[3-8]*.jsonl.gz` first, then the tennis, hockey_nhl and basketball files for 17 and 18 Nov. Do not overwrite any file that is newer locally.
(c) Paste: `ls -l --time-style=full-iso` of each directory (first and last 3 lines, plus `ls | wc -l`) and `df -h /mnt/HC_Volume_107257520`. Check space first: copy-back must leave 15 GB free; if not, copy esports 18 Nov only and tell me the size of the rest.
Done check: paste under `## P57 goalserve hold and copy-back (19 Nov)` in `agent/status/goalserve.md`.

I will not change the capture. The probe v3 (running) is unaffected.
