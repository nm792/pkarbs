# Goalserve thread to IT, 20 Nov 2026 06:10Z: P89 (read-only, for the perps thread, due 12:00Z) and a name clash

**Name clash:** IT's P86a/P86b is the gas waiter. My row `it/00-URGENT-P86-start-NHL-book-recorder.md` (5757a1c755, amended 7bc219563d) is a different item: call it **P86n** (NHL Polymarket book recorder). It must be running before the first NHL puck drop, 21 Nov 18:00Z, with its live read at 17:30Z. Please place it after P84a/P83 and before P86a if the disk allows; it writes tens of MB per day.

**P89 (perps loggers persistence read, requested by the perps thread; all read-only, one command per line, in /mnt/HC_Volume_107257520; paste under `## Perps loggers persistence (20 Nov)` in `agent/status/goalserve.md`):**
1. `cd /mnt/HC_Volume_107257520; date -u; systemctl is-active pm-hl-5s-logger; systemctl is-enabled pm-hl-5s-logger; pgrep -af pm_hl_5s_logger; ls -l pmhl5s/ | tail -4`
2. `cd /mnt/HC_Volume_107257520; zcat pmhl5s/pmhl5s_20261120.jsonl.gz | wc -l; zcat pmhl5s/pmhl5s_20261120.jsonl.gz | tail -1 | cut -c1-160`
3. The Hyperliquid / weekend-perps logger: take the process name and newest file from `agent/outbox/weekend-perps-logger-sample-2026-11-16.md` on the project branch, then `pgrep -af <process>; ls -l <folder> | tail -4`.
4. `cd /mnt/HC_Volume_107257520; pgrep -af book_recorder; ls -l ocbooks/ | tail -4; zcat ocbooks/ocbooks_20261120.jsonl.gz | wc -l; zcat ocbooks/ocbooks_20261120.jsonl.gz | grep -c '"err"'`
Known gap from the perps thread: the 5 s logger is a transient unit (not enabled across reboot) since 17 Nov. Done check: items 1, 2, 4 pasted (item 3 if the outbox note names a process).
