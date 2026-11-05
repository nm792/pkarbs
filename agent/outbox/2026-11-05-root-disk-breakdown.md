# from_agent/outbox: root disk breakdown + safe cleanup (12:40Z ruling, step 1-2)

Round 2026-11-05T12:32Z. Executed the 12:40Z ruling steps 1-2 (breakdown + safe cleanup). Tennis relaunch per step 4: HC volume.

## RESULT
- Root `/` freed **5.9 GB -> 7.1 GB free** (81% used) this round via safe cleanup only.
- Cleanup done (all committed/repo-verified, nothing running touched):
  - `/root/hltvcap/run1-2026-11-04` (891 MB) deleted — raw is committed+gzipped on origin/claude/project-thread-6tydow `live/cs2_feeds/raw/hltv-2026-11-04/` (all 5 files, 32 MB gz).
  - apt lists + archives (`rm /var/lib/apt/lists/*`, `apt-get clean`) ~+0.3 GB.
  - pkarbs `tmp_pack_*` garbage (128 KB) removed.
- journald 108.8 MB < 200 MB vacuum target -> vacuum freed 0 (already under).

## DATA — `df -h /` = 7.1 GB free / 81% (was 5.9/84%). HC volume = 21 GB free / 57%.
- /tmp is **tmpfs (RAM)**, 2.8 GB — deleting frees RAM, NOT root; excluded from root reclaim (noted honestly).
- Biggest root consumers still on `/`: /root/mfw-clone 3.3G (git packs 2.5G), /root/pkarbs 2.3G (git 1.6G), /root/polymarket-temperature-trading 1.9G, /root/sports-maker 1.6G, /root/bf-sweep-293 1.2G, /root/nautilus 1008M, /root/audit-push-wt 956M (git worktree of mfw-account-backfill, dialogue data duplicating origin), /root/.hermes 956M, /root/dialogue-push-wt 923M (git worktree, dialogue dup), /root/hltvcap 891M->now 0, /root/biotech 574M (archived repo, kept).
- Running captures on `/`: cricket-feeds (344M, main consumer, leave running per ruling step 5), hko/n050 loggers, nc380 shadow (spool on HC).

## OPEN / NOT VERIFIED
- `>= 12 GB free on / before 20:00Z` NOT reached (7.1 GB). Remaining levers are git repositories/worktrees and /root loops holding the fleet's own checkout + data — offloading them is a bigger judgement call (move whole repo dirs to HC volume / storage box), which I'll stage next rather than guess under the repetition cap. Stated honestly: safe cleanup alone gets ~7 GB, not 12; reaching 12 GB needs moving at least one multi-GB repo/worktree dir (e.g. audit-push-wt 956M, dialogue-push-wt 923M worktrees whose dialogue data fully mirrors origin) to the HC volume.
- tennis relaunch (step 4): HC free 21G >= 20G gate -> relaunched on HC volume 12:33Z (systemd unit tennis-books-hc, MemoryMax 500M, timeout 32280s ~ 21:30Z stop). First probe rows present (clob_rtt). Hourly gzip+commit from HC dir to continue.
- Confirm at 20:00Z in heartbeat: / free, HC free, which captures run, LoL/CS2 write to /.

## Count
notes run 1 (12:40Z ruling steps 1-2, step 4 relaunch), applied 2, outstanding 1 (12 GB target).
