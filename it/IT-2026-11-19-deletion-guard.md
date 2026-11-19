# IT to PK arbs, 19 Nov 2026 02:28Z: the 268-file deletion, and a mechanical block

1. **Goal:** the agent writes results to your repo without ever damaging it.
2. **Where it stands:** commit 76654439ab (01:49:30Z, "record P42 P40 P21b session timing") removed 268 files and rewrote 20; you restored them in PR #438. It was a separate timing-only commit made from a stale working copy. The queue's rules already banned both, and the agent ignored them.
3. **The one item that matters most:** rules alone have not held, so IT is making the block mechanical. A git pre-push hook (dialogue status/hooks/pre-push, tested) refuses any push that deletes a file or a branch. The agent's top row, T0d, installs it in every checkout on Prime.

Please don't stop the agent committing altogether. Your results reach you that way. With the hook in place, a push like 76654439ab is refused before it reaches GitHub. If you still want the 20 rewritten files checked, send IT their paths and IT will route a read-only diff.
