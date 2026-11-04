# 4 Nov ~11:55Z from thread "Time HLTV live scoreboard on CS2": please start agent/tasks/hltv-scorebot.md run 1 now

Nick approved scraping HLTV's live scoreboard (4 Nov 11:31Z). Please run "Run 1" in agent/tasks/hltv-scorebot.md as soon as
you read this (it ends itself at 16:00Z), do the 13:20Z check, copy raw files every 30 min to live/cs2_feeds/raw/hltv-2026-11-04/,
and write agent/status/hltv-scorebot.md. Read-only, one node process, 400 MB cap. Do NOT start run 2 until this thread says go.
If `npm ci` cannot reach the npm registry, say so in the status file and stop.
