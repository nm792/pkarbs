# CHUNK C (one P row): run the Goalserve stored-odds inventory. Read-only, no capture change. Posted 17 Nov 07:55Z

Why: Nick asked which bookmakers, markets and update rates are really in the stored esports odds bodies (13-17 Nov), and whether Pinnacle appears. No key needed.

Commands (from the repo root, on the Finland server):
```
python3 -I feeds/test_goalserve_inventory.py
python3 -I feeds/goalserve_inventory.py --files '/mnt/HC_Volume_107257520/pkarbs/goalserve/esports_payloads/esports_2026111[3-7]*.jsonl.gz' --out agent/status/goalserve-odds-inventory-2026-11-17.md
```
If the hour files live elsewhere, `ls -d /mnt/HC_Volume_107257520/pkarbs/goalserve/*payloads*` and adjust the glob.

Done check: test prints ALL PASS; the status file exists and its first bullet reads files read >= 5 and stored payload rows > 0, and its last line starts `PINNACLE in stored in-play bodies:`. Commit the status file and post its last line and the bookmaker section in the PR.

Also post (read-only, item 1e) the output of:
```
ls -la /mnt/HC_Volume_107257520/pkarbs/goalserve/ | head -50
ls /mnt/HC_Volume_107257520/pkarbs/goalserve/*payloads* | tail -20
grep -rl -i websocket live/ | head
```
so we know whether tennis or hockey bodies or any WebSocket recording exist.
