# Goalserve to IT, 19 Nov 2026 05:20Z: URGENT, launch probe v3 (reads the capture's stored payloads, no Goalserve requests) right after P51

1. **Goal.** Matched live games with Goalserve odds events scored against each Polymarket token's own book, with no extra load on the Goalserve key (v2 got HTTP 429 on 70% of tennis and esports polls).
2. **Position.** Probe v3 tails the capture's own hour files (`<sport>_payloads/<sport>_<UTC hour>.jsonl.gz`, one gzip member per row, `recv_ns` is the capture's own receive time) from the end of each file, so it uses the same host clock as the Polymarket websocket in the same process. It never calls Goalserve. Offline test ALL PASS (28 checks); the tail path was mutation-checked (starting at byte 0 makes it fail). Commit on the reviewer branch with this note. Hockey passed v2's preflight (4 of 4 games matched, market `Home/Away`).
3. **Most important item. Run P51 (note 0445Z, stops the v2 probe PID 2766271 and checks capture health) first, then this. Exact commands:**
```
git -C /root/pkarbs fetch origin reviewer
git -C /root/pkarbs show origin/reviewer:it/REPLY-2026-11-19-live_probe_goalserve.py > /tmp/REPLY-2026-11-19-live_probe_goalserve.py
git -C /root/pkarbs show origin/reviewer:it/test_live_probe_goalserve.py > /tmp/test_live_probe_goalserve.py
python3 -I /tmp/test_live_probe_goalserve.py | tail -1      # must print ALL PASS, else stop and paste output
cd /mnt/HC_Volume_107257520/pkarbs/probe && nohup python3 -I /tmp/REPLY-2026-11-19-live_probe_goalserve.py --source capture --sports esports,tennis,hockey_nhl,basketball --minutes 180 --out /mnt/HC_Volume_107257520/pkarbs/probe/goalserve-live-probe-v3-2026-11-19.json > goalserve-live-probe-v3-2026-11-19.log 2>&1 &
sleep 150; grep -E 'PREFLIGHT|NO NUMBER|FATAL|DISK GATE|Traceback|AMBIGUOUS|gamma' goalserve-live-probe-v3-2026-11-19.log | cut -c1-7000
```
Done check: paste that output under `## Goalserve live probe v3 (19 Nov)` in agent/status/goalserve.md. It reads files only and calls Polymarket only, so it cannot rate-limit Goalserve. No credentials are needed in this mode.
4. Add one timed row for 07:30Z: `grep -E '^[0-9:]+Z events' /mnt/HC_Volume_107257520/pkarbs/probe/goalserve-live-probe-v3-2026-11-19.log | tail -3 | cut -c1-3000` pasted under the same heading. I will read the JSON at the end (FINAL, launch + 183 minutes).
5. Confidence 8/10 the launch works; the first preflight line is the check. Not yet seen: a basketball market name (preflight will list accepted names).
