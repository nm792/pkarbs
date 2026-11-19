# IT 19 Nov 17:10Z: P77 incident, box copy of ts_mqtt overwritten; P77r snapshot check routed

1. **Goal:** PK arbs captures live sports feeds and Polymarket books to measure feed-vs-market lead for arbitrage, without losing the capture data.
2. **Where it stands:** P78 done (a525dfab); P76 done (51c4acef, corrected 8d3418e3): perp open-contract recorder PID 2701410 running, 18,578 rows, first 03:30:28Z, last 16:41:59Z, 0 err rows. The agent itself notes its `"t": 17` count does not prove the 14:30Z open was captured; only the first-last span is shown. P77b growth series running since 16:41:43Z (PID 3763087, ends about 17:42Z).
3. **The item that matters most:** the only verified archive copy of the dead TheSports feed was destroyed. At 16:38-16:39Z both local files were already 0 bytes (mtime 14:59:45Z), so the IT script's guard exits with "nothing to do". The agent then ran its own rsync at 16:39:36Z and overwrote the box copies (ts_mqtt.jsonl 17,088,904,344 B; ts_poll.jsonl 57,645,071 B) with empty files (pkarbs 8d3418e3, agent's own correction). No local truncation ran. No commit records who emptied the local files at 14:59:45Z or who made the earlier box copy, so that is unsupported.

## Items
- Routed P77r (top PK arbs row, read-only, dialogue 1c2570e3): list the box's .zfs snapshots and, from the newest one taken before 16:39Z, the final-topics-32295b folder. It copies and restores nothing. Nick is asked in NEEDS-NICK to check box snapshots and to name one to restore.
- If no snapshot exists, the MQTT payload before 14:59:45Z is lost. Please say whether your analysis still needs it, and whether to drop the files from your plan.
- Order after P77r: P77b paste, then P67, P75, P60c, P68a, P66, P59, P60b, P54c, P55t (unchanged).
- Open with you: P16s (the stash ruling on 1,978,186,746 untracked bytes, gate report 81d3ad3f) and P4 (NVDA partial, 6cd69906).

Times from `date -u`. Figures from pkarbs agent/status/goalserve.md at 8d3418e3.
