# RELEASE P122b: Nick approved (23 Nov 13:53Z, "yes", via coordinator, INBOX P-DOTA-9)

This supersedes the HOLD note it/REPLY-2026-11-23-1355Z-HOLD-P122b-until-Nick-approves.md.

1. Run P122a (read-only pre-flight, bash feeds/preflight_pmdota.sh on the merged code 353787e35f). Exit 0 = PASS. Any other result: do NOT restart; post the output.
2. Only on PASS, run P122b: restart pmdota with the exact old command line on 353787e35f. Save the old script as pm_dota_books.js.old. Keep all files. Expected gap 5-10 s.
3. Within 15 minutes post a HEALTH READ: log line "discovery markets N tokens 2N" with N>0, one node pid, books.jsonl size at two reads 60 s apart during a live game, df of /mnt/HC_Volume_107257520.
Do not write any logic.
