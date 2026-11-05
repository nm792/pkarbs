# Ruling on your open item: get `/` from 7.1 GB to >= 12 GB (outbox/2026-11-05-root-disk-breakdown.md)

From the project thread, 12:50Z 5 Nov. Good work: cricket snapshot committed (cb824e15), tennis relaunched on HC, 5.9 -> 7.1 GB. Approved: stage the moves yourself, no new note needed. In this order, stop as soon as `/` >= 12 GB free:

1. **Remove the two dialogue worktrees** /root/audit-push-wt (956M) and /root/dialogue-push-wt (923M), only after `git -C <dir> status --porcelain` is empty AND `git -C <dir> log @{u}..` shows nothing unpushed. Use `git worktree remove`. If either has uncommitted or unpushed work, commit+push it first, then remove. (~1.9 GB)
2. **Move to the storage box, then delete local**, three-way sha256 as in the 3 Nov offload ruling (tar each dir, local sha, box sha, manifest line committed). Order: /root/biotech (574M, archived), /root/bf-sweep-293 (1.2G), /root/sports-maker (1.6G), /root/polymarket-temperature-trading (1.9G). Skip any dir with an open file (`lsof +D`), a running process, a systemd unit, a cron entry using it, or mtime < 48 h; say which you skipped and why. Keep a one-line README/symlink note locally saying where it went.
3. **Do not touch:** /root/mfw-clone, /root/pkarbs, /root/nautilus, /root/.hermes, the cricket dir, tennis HC dir, tonight's LoL/CS2 logger dirs, any key or config. Git pack trimming (`git gc`) is allowed on /root/pkarbs only if nice/ionice and it frees >= 300 MB; otherwise skip.
4. Report in `agent/outbox/2026-11-05-root-12gb.md`: each step's GB freed, `df -h /` after, anything skipped. If 12 GB is not reachable without touching section 3, say so with numbers. The hard floor for tonight is 6 GB at 22:00Z; 12 GB is the comfortable target.
5. Keep hourly cricket and tennis commits going (delete committed raw each time). Cricket capture ends ~17:15Z.

Nick can overrule directly. Never commit keys.
