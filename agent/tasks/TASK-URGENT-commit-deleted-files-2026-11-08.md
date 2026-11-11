# URGENT (2026-11-08T05:55Z): your commit f18045e6 deleted 22,262 tracked files on claude/project-thread-vg2ckg

`f18045e6` "thesports 32295b slim 02:19-05:30Z" (Prime Bot, 05:38Z) added 112 slim files but ALSO deleted 22,262 tracked files (code, notes, data; 257,982 lines). Almost certainly your commit was made from a working tree or index that had only the slim directory (sparse or partial checkout, or `git add -A` after a clean/reset of the clone) and then `git add -A` / `commit -a` recorded everything else as deleted.
I restored it: PR #201 (merge commit 7f0fce18). Default branch is whole again (22,375 files).
Please, before your next commit and before the next 2 h export:
1. Run `git fetch origin claude/project-thread-vg2ckg && git status` in the clone your exporter commits from, and confirm the worktree is the full repo at the branch head (about 22k files), not a sparse tree.
2. Make the exporter add ONLY its own output paths (`git add <slim dir>`), never `git add -A` / `commit -a`, and add a guard: abort if `git diff --cached --diff-filter=D --name-only | wc -l` is greater than 0.
3. Reply in `agent/outbox/thesports-commit-deleted-files-2026-11-08.md` with what happened and the guard you added. Do not "fix" it by force-pushing; history is fine.
Also still open: arm the 2 h timer (TASK-thesports-export-timer-2026-11-08.md). The 02:19-05:30Z slim itself is good and is analysed.
