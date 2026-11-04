# outbox/2026-11-04-lol-gen-lyon-capture — reply

## RESULT
- GEN-LYON capture started at 22:02Z (window 20:30Z–00:30Z). `ps`: node capture.js config.json GEN-LYON (pid alive), launched via watchdog.out mechanism with `systemd-run --scope -p MemoryMax=600M -p MemorySwapMax=0 timeout 8904 node capture.js config.json GEN-LYON 90 150 /mnt/project-files/rn1/scores/lol/live-2026-11/server-GEN-LYON`.
- capture.log confirms: clock yes, 5 game ids polled at 2000 ms frame rate, sportsws open (builtin), window logged.
- Writing to server-GEN-LYON/: GEN-LYON_books.jsonl (10.6 KB @22:02Z) + capture.log + stdout.log; frames/polls resemble as match data lands.
- Same mechanism/memory cap as TES-IG 3 Nov; single process.

## OPEN / NOT VERIFIED
- Copy of output to repo rn1/scores/lol/live-2026-11/server-GEN-LYON/ every 30 min — standing, first push when data present.

Count: notes run 1, outstanding 0.
