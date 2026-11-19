P68b — TheSports folder identification (19 Nov 2026)

Read-only inspection completed at 14:04Z. No files were shipped or deleted, and no process was stopped.

- The only immediate entry under the TheSports directory was `final-topics-32295b`, measured at 49G by `du -sh`.
- The requested last six listing lines are recorded in `agent/status/goalserve.md` under `## P68 thesports folder (19 Nov)`.
- The active capture unit (PID 3243761) writes TheSports MQTT/poll files and Polymarket books/markets in the same process. The separate trades unit (PID 3243759) also writes `trades.jsonl`. Both units were active; books and trades were still growing on the 14:05Z stat. No stop was attempted because the capture process combines the protected Polymarket book recorder and TheSports feed writer.
- Other matching processes at the read time were the two-hour export timer and its active export process; they were left untouched.

Evidence: `agent/status/goalserve.md`, P68 section. The P68b output is pushed with this report.
