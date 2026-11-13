# 2026-11-10: clause 22 (split by work type / daily change batch) is live

Cross-project governance change, adopted and pushed on the dialogue repo (`nm792/trading-test.git`, `origin/dialogue`, commit `bfc09e2782fb38933bb7786982ccfcd21fe72c65`) via reviewer note X417.

CHARTER.md now carries **clause 22**: work that must not run from overnight plans (new units/loggers, installs, code/config changes, crontab edits, deletes, key/branch changes) is collected in `dialogue/CHANGE-BATCH.md`, numbered one line per item (what/why/revert/project), listed at the top of the morning report, and applied only after Nick's single reply.

**This project (pkarbs) has one open type-B item in CHANGE-BATCH round 2026-11-10:**
- **#1 — pkarbs capture scheduler**: "Enable the no-systemd capture scheduler: call `python3 agent/tasks/schedule_captures.py --run-due` once per ~15-min round". Marked **install only after Nick taps** (409 gate 11-08..11-15). Revert: disable the scheduler call.

Nothing actionable in this repo until the approval lands; file stands as notification only.
