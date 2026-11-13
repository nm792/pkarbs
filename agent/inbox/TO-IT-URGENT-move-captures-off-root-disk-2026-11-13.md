# TO IT, URGENT, 13 Nov 2026 15:35Z: move the PandaScore and Goalserve captures to the data volume TODAY

Source: agent/status/pandascore.md (15:17Z) and agent/status/goalserve.md. Hermes found that `/vol2` resolves to the ROOT volume (`findmnt -T /vol2` -> `/dev/sda1` on `/`). The 98 GB data disk is at `/mnt/HC_Volume_107257520`.

Why this is urgent:
- CHARTER: no data on the root disk. Both live captures currently write there.
- Free space on `/` was 17,564,192,768 B (about 17.5 GB) at 15:12Z. The PandaScore client stops itself at 15 GB free, so about 2.5 GB of headroom. Goalserve esports changed-payload store measured 279 MB/day compressed, on top of the other Goalserve and recorder writes. Either capture can auto-stop before the LoL Worlds final on 14 Nov, and PandaScore's trial runs to 1 December (BLAST Slam Dota from 17 Nov).
- PandaScore expected size: first-hour measure is due about 16:12Z (file size and row count of `/vol2/pandascore/raw/pandascore_2026111315.jsonl.gz`); I will add MB/day to issue #283 when it lands. Until then treat it as unknown, not small: 10 sockets, state pushed on every kill or round change.

Please, today:
1. Rule where both captures write (the data volume, or the storage box per charter) and give the exact path.
2. Move or symlink `/vol2/pandascore/` and `/vol2/goalserve/` to that path, with the capture processes restarted and the gap stated (PandaScore tmux `pandascore`, Goalserve tmux `goalserve`). No data may be lost in the move; verify row counts before and after.
3. Update the disk-floor guards to check the NEW volume, not `/`.
4. Post the result in agent/status/pandascore.md and agent/status/goalserve.md, and reply on issue #283.

Nick approved both captures today (inbox 2026-11-13-pandascore-capture-APPROVED.md, goalserve esports APPROVED). This note only asks IT to fix where they write.
