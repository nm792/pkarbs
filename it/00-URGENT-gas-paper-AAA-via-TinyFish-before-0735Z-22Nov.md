# 00-URGENT for IT: AAA page log via TinyFish, before 07:35Z 22 Nov 2026

Why: the direct AAA fetch returns Cloudflare 403 (435 of 435 rows). Nick approved reading the page through TinyFish Fetch (his message 22 Nov 02:26Z; Reviewer R-018). Do not change headers, UA or proxy on the direct logger.

1. Deploy `scan/gas_window/daily_rule/aaa_page_tinyfish.py` and `test_aaa_page_tinyfish.py` from commit 9f7731e739d7f571fd3b72937f6a2f73d2fa2f5d (branch claude/project-thread-lfb1pf, 7 checks, tested locally). Paste the test output.
2. It needs env `TINYFISH_API_KEY` (the Fetch API is `POST https://api.fetch.tinyfish.ai`, header `X-API-Key`). If the server has no TinyFish key, say so in agent/status/gas.md at once; do NOT ask Nick for the key text in chat, tell the coordinator.
3. Run it for 22 Nov, one read per minute, same output file the paper adapter reads (`/mnt/HC_Volume_107257520/gas/aaa_page_2026-11-22.jsonl`):
   `python3 aaa_page_tinyfish.py --out <that file> --start-epoch <07:40Z epoch> --until-epoch <09:00Z epoch> --interval 60`
   (run_paper_window.sh also starts the old direct logger to the same file; give the TinyFish rows their own file or stop the direct logger for 22 Nov, and tell me which, because paper_post reads one page file and a 403 row never counts.)
4. 15-minute sanity at 07:55Z: page rows with status 200, price and 'Price as of' date, and row count twice 60 s apart; books pid and books size twice 60 s apart (books window starts 07:40Z by run_paper_window.sh, cron 07:35Z; the 21 Nov books stop at 09:29:59Z was the 04:30 ET window end, not a crash). Post both in agent/status/gas.md before 07:50Z (books) and 08:30Z (sanity).
5. Paper only. No orders.
