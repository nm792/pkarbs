# Goalserve to IT, 19 Nov 2026 02:15Z: URGENT, run the live probe now (before P35/P30/P37)

1. **Goal.** One process, one clock: Goalserve in-play odds vs each Polymarket token's own book (websocket), on games live now, esports, tennis and NHL. Exploratory, UNCHECKED. Nick asked for this as a probe done properly; no queue wait.
2. **Position.** Code is committed with its offline test: `it/REPLY-2026-11-19-live_probe_goalserve.py` and `it/test_live_probe_goalserve.py` (test ends ALL PASS, about 2 s). Probe is modelled on the CS2 probe; reads creds from `/etc/pkarbs/goalserve.env` and never prints them.
3. **Most important item. Exact commands (read-only, small output, no edits to logic):**
```
git -C /root/pkarbs fetch origin reviewer && git -C /root/pkarbs show origin/reviewer:it/REPLY-2026-11-19-live_probe_goalserve.py > /tmp/probe_gs.py
git -C /root/pkarbs show origin/reviewer:it/test_live_probe_goalserve.py > /tmp/test_live_probe_goalserve.py; cp /tmp/probe_gs.py /tmp/REPLY-2026-11-19-live_probe_goalserve.py
python3 -I /tmp/test_live_probe_goalserve.py | tail -1        # must print ALL PASS, else stop and paste output
cd /mnt/HC_Volume_107257520/pkarbs && mkdir -p probe && python3 -I /tmp/REPLY-2026-11-19-live_probe_goalserve.py --sports esports,tennis,hockey_nhl --minutes 90 --out /mnt/HC_Volume_107257520/pkarbs/probe/goalserve-live-probe-2026-11-19.json 2>&1 | tee /mnt/HC_Volume_107257520/pkarbs/probe/goalserve-live-probe-2026-11-19.log
```
(`git fetch` and `git show` only read; no stash, no checkout in /root/pkarbs. The test file must sit in the same folder as the probe script, so the test is copied to /tmp under its repo name too.)
4. **Done check (within 15 minutes of start):** paste the line starting `PREFLIGHT` and any `NO NUMBER for` lines into agent/status/goalserve.md under `## Goalserve live probe (19 Nov)`, then commit. Paste the 5-minute summary lines every 30 minutes and the `FINAL` line at the end. If the process exits, paste the last 20 log lines. Disk gate inside the script refuses under 15 GB free.
5. Confidence 8/10 the script runs as intended: offline test covers parsing, mapping, own-token, planted edges both ways and a failing preflight. Not yet exercised against the live feeds; the first PREFLIGHT line is that check.
