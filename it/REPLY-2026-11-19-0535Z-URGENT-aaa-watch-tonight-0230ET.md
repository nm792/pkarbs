# IT, 19 Nov 2026 ~05:35Z: URGENT run aaa_watch.py tonight, start by 07:30Z (02:30 ET)

SETTLED.md read at commit e2a25c41beffd3f4438590a691fc2ed07402838b.
Goal: find and build un-publicised, automated edges toward $500/day. Nick's position (19 Nov 05:29Z): the daily jump in the Polymarket gas markets is the AAA data release at about 03:15 ET (08:15Z in November). Polymarket trades show a sweep of winner tokens at 03:14 to 03:36 ET on 24 of 28 days. To trade it we must see the AAA page change ourselves, with timestamps.
The ask (one step, committed code, no edits): run the committed watcher on the server from 07:30Z to 09:00Z on 19 Nov.

```
cd <pkarbs checkout at default branch, commit 71bd42c3 or later>/scan/gas_window
python3 test_aaa_watch.py          # must print: 3 of 3 tests pass
python3 aaa_watch.py --out /mnt/HC_Volume_107257520/gas_watch --until 2026-11-19T09:00:00Z --interval 5 --max-seconds 5400
```

- Start before 07:30Z. Reply with the start time (UTC) and the first 3 lines of /mnt/HC_Volume_107257520/gas_watch/aaa_watch.jsonl within 15 minutes of starting. No data on the root disk.
- What it records: for every poll (5 s) the receive time in ns, HTTP status, Date / Last-Modified / ETag headers, body hash, and the parsed "Price as of" date and the Regular current / yesterday / week-ago averages. I will read the file for the minute the "Price as of" date or the Current Avg. changes.
- IMPORTANT, plain facts: from my cloud session, a plain GET of https://gasprices.aaa.com/ returns HTTP 403 from Cloudflare. If it is 403 on the server too, do NOT change the user agent, add headers, or use proxies to get round it. Let it run and log the 403s (that is the result), then tell me the status codes seen. If the server gets 200, great.
- I am separately recording the Polymarket books for the same night (committed pm_gas_books.py); nothing needed from IT for that.
- Code: scan/gas_window/aaa_watch.py (blob a2cd54b1), test_aaa_watch.py (blob e7df4955). The parser was tested only on a synthetic page shaped like the table in the Polymarket rule text, not on the real page: a null parse with a changing hash is still usable.

Confidence 8/10 that the command is correct; 5/10 that the server is not Cloudflare-blocked as well.
