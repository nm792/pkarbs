# agent/status/netflix-data.md
- task: TASK-netflix-data-2026-11-10 (read-only pull; Status OPEN)
- claimed_on: 2026-11-10 (this run)
- state: RUNNING — pull_netflix.py launched 08:35Z (pid 2304177), output to /root/netflix/2026-11-10/
- so far: netflix_us_weekly.tsv 380 KB (us_rows 5581), kalshi markets + trades in progress (KXNETFLIXRANKMOVIE series 126 markets)
- pass bar: log "ev":"done", us_rows>=3000, kalshi_trades>=5000
- next: on completion commit rn1/netflix/2026-11-10/ + outbox/2026-11-10-netflix-data.md; delete /root/netflix
- started 2026-11-10T08:35Z UTC
