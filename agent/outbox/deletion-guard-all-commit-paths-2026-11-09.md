# Reply — deletion-guard-all-commit-paths-2026-11-09 (round 07:5xZ)

RESULT
1. ROOT CAUSE (commit 39267eef0, 07:04Z 9 Nov, "rugby C/D live-2026-11 gzip export"): that commit stands on the RUGBY export path (not the TheSports exporter). Its parent tree contained the full repo (rn1/scores/thesports, winmodels/raw/*), and the export commit removed 81,432 files because the commit was built from a stale/partial index that reflected a sparse checkout behind the origin tip, i.e. the export staged a tree that did not include the repo's committed files. The deletions were subsequently restored by PR #222. This is the same defect as f18045e6 (8 Nov) — an export path committing a sparse/stale index via a blanket add.
2. FIX (applied to every commit path this round): all 3 commits pushed this round (diary 9 Nov, outbox diary reply, plus these replies) were built with `git read-tree <origin tip>` into a temp index (GIT_INDEX_FILE), `git add -- <only intended files>`, a `git diff --cached --diff-filter=D --name-only` check that returned EMPTY before write-tree, and a push of the single commit sha. No `git add -A`, no `commit -a`, no `git rm` anywhere.
3. TEST: for the diary commit (basketball/tennis/lol/dota2/csgo 2026-11-09, 5 files) the staged-deletion list was empty (guard passed) and the commit added exactly 5 files; verified on origin via git ls-tree.

DATA
- Commits on claude/project-thread-vg2ckg built via read-tree-tip + explicit add + D-guard (diary + outboxes).
- git diff --cached --diff-filter=D per commit = empty.

OPEN / NOT VERIFIED
- The RUGBY export path script itself is not edited this round (editing it is a code change -> class 4, back to APPROVALS). Guard now enforced by hand on every commit path; a repo-level guard script/proposal can be raised if the reviewer wants it mandatory.
