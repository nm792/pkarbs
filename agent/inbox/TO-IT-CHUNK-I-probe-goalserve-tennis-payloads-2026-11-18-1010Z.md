# CHUNK I: probe the stored tennis payloads (market names, league strings, counts). Read-only. Posted 18 Nov 2026 10:10Z. Needed today so tennis can be pre-registered.

**1. Goal.** Time Goalserve tennis in-play odds against the Polymarket price in the free trial, in parallel with esports (Nick, 08:04Z).
**2. Position.** Chunk H showed the capture running (4908eea2a6) and tennis hour files present, outer keys `body`, `recv_ns` as for esports. I need the market names and league strings in the tennis body before I can fix the test cells. The probe reuses the v2 test's own parser; it prints counters only, no cells and no verdicts, and tested here on a fake file.
**3. One item.** Use the clean export (it/REPLY-2026-11-18-URGENT-goalserve-ruling-clean-tree-no-stash.md, six lines) so `feeds/gs_sport_probe.py` exists at `$X/feeds/`, then run and paste the full output under `## I tennis probe (18 Nov)` in agent/status/goalserve.md:
```
G=/mnt/HC_Volume_107257520/pkarbs/goalserve
ls $G/tennis_payloads | grep 2026111806 ; ls $G/tennis_payloads | grep 2026111807
TMPDIR=$V/tmp nice -n 10 timeout 1800 python3 -I $X/feeds/gs_sport_probe.py "$G/tennis_payloads/tennis_202611180[67].jsonl.gz" "$G/goalserve_20261117.jsonl" 1794981600 1794988800; echo exit=$?
```
(The 18 Nov polls are in `goalserve_20261117.jsonl` because the log name is fixed at capture start. If the hour files are no longer local, use the box copy of the same two hours.) No key, URL or credential is printed.
**Done check:** `exit=0`, lines `files 2`, `events N`, `market_names_used`, `league_prefixes_seen`.
