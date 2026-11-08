# Inbox: one-shot reachability check of cross.bet from the server (no process, under 1 minute)

From: Claude, PK arbs thread "Find kill-speed CS2 data via betting sites" (4 Nov 2026 10:45Z).
Why: cross.bet's Cloudflare firewall blocks our US cloud IP. We need to know if the server's IP gets real pages.
Question / pass-fail: PASS if `https://cross.bet/` returns HTTP 200 with a page that is not a Cloudflare block page.

Please run, from the server, and paste the output into agent/outbox/crossbet-reachability.md:
```
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
curl -sS -m 15 -o /tmp/cb.html -w "%{http_code}\n" -A "$UA" https://cross.bet/
grep -o '<title>[^<]*' /tmp/cb.html; grep -oiE 'esport|counter-strike|cs2|in-play|live' /tmp/cb.html | sort | uniq -c
curl -sS -m 15 -o /dev/null -w "%{http_code}\n" -A "$UA" https://cross.bet/robots.txt
rm -f /tmp/cb.html
```
No loop, no install, nothing left running. Do not log in or create anything on the site.
