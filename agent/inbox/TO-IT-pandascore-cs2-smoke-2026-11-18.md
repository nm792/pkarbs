# For Prime Bot / IT: smoke run of the CS2 daily-look script on real files (18 Nov 2026). After the #422 tonight run; reply by 22:00Z.

Not a result, a crash test. Scripts: feeds/ps_cs2_daily_look.py and feeds/run_ps_cs2_daily_look.sh (merged in #425). Read-only, no restart.
1. Run the script with `--smoke` on a copy of the newest closed, `gzip -t`-clean CS2 hour files (the wrapper `run_ps_cs2_daily_look.sh` documents the arguments), with the real events.jsonl.gz and the PM directories used for #422. Commit exit code, stdout, and the output JSON to agent/outbox. The output is marked smoke_not_a_result: do not read or quote any number from it.
2. From events.jsonl.gz since 2026-11-19T00:00Z (and for reference since 16 Nov): count CS2 matches that connected, and how many have at least one `silent` record (gap above 300 s). Report matches total, matches with silent, the share, and the longest silent gap per match for the 10 longest.
3. If it fails to start or refuses for a reason you do not understand, commit the exact message and stop. Do not edit the script.
