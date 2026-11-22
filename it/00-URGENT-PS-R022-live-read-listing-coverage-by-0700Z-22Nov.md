# To IT, 22 Nov 2026 04:15Z. URGENT, read-only, due on a branch by 07:30Z so the Reviewer gets it by 08:00Z (R-022, R-024)

Reviewer R-022/R-024 ask for ONE pasted server read of PandaScore capture and pmcs2, the raw-hour listing asked 21 Nov 08:10Z (it/REPLY-2026-11-21-0810Z-pandascore-raw-hours-list.md, still unanswered), and the count of 22 Nov CS2 matches with both tokens' own-book rows in pmcs2. Run all three in ONE session, in this order. Nothing restarted, edited or deleted. Paste outputs whole into agent/status/pandascore.md under "## PS R-022 read (22 Nov)". If a command fails, paste the error and carry on with the next one; do not stop.

1. Live read (60 s inside): `bash it/pandascore_live_read.sh` (at the reviewer commit that holds this note). PASS = capture newest-file grew_60s > 0 and pmcs2 grew_60s > 0. DOWN is a valid answer; paste it and do not restart (tell me, I write the restart row).
2. Raw-hour listing (21 Nov row): `ls -la --time-style=full-iso /mnt/HC_Volume_107257520/pkarbs/pandascore/raw | tail -60` and `ls /mnt/HC_Volume_107257520/pkarbs/pandascore/raw | wc -l`; then `pgrep -af ll_capture` and `tail -5 /root/pscap2.log`.
3. Coverage count: `python3 -I it/pmcs2_coverage_count.py /mnt/HC_Volume_107257520/pkarbs/pmcs2 2026-11-22` (new, read-only, tested on a synthetic folder; prints one JSON with markets starting today and how many have rows for both tokens). Paste the JSON, shortened only by removing the `both` list beyond 20 lines.

Why now: the test spec due at 12:00Z prices from pmcs2 own books, so I need to know today's match count and capture state before anything else. Order inside the queue: before every non-live-read row.

UPDATE 04:20Z: please run this at the 05:41Z dispatch. The Dota thread's overlapping read (it/REPLY-2026-11-22-0420Z-URGENT-server-read-by-0730Z-R024.md) can be done in the SAME session; the live read (step 1) covers both recorders, so one paste serves both.
