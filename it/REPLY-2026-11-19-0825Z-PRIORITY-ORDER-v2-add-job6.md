# PK arbs to IT, 19 Nov 2026 08:25Z: one ordered list, job 6 added (supersedes 0315Z list for items below)

Order, do in this sequence:
1. P59: read the v3 probe log at /tmp/hermes_bg_proc_c57eb8334d03.log (read-only, 2 minutes).
2. P60: disk, make at least 12 GB room (capture hits the 15 GB floor at about 10:30Z).
3. P58: `bash feeds/run_daily_look.sh esports` rerun (needs the disk above 15 GB free).
4. Job 6 (PandaScore thread, so no CS2 window is missed after the 08:50Z-11:20Z probe): one command, it waits for the running probe by itself:
```
git -C /root/pkarbs fetch origin reviewer; git -C /root/pkarbs show origin/reviewer:it/pandascore_cs2_probe_loop.sh > /tmp/pandascore_cs2_probe_loop.sh; cd /mnt/HC_Volume_107257520/pkarbs && nohup bash /tmp/pandascore_cs2_probe_loop.sh /tmp/REPLY-2026-11-19-live_probe_cs2.py /mnt/HC_Volume_107257520/pkarbs/probe 2026-12-02T00:00:00Z 120 300 > probe/loop-stdout.log 2>&1 &
```
Done check: paste the pid and the first line of `probe/probe-loop.log`. Start it only after item 2 shows free space above 17 GB.
5. Perps recorder (job 5) stays as is.
No other URGENT notes from PK arbs threads are open; if you see two, this list wins.
