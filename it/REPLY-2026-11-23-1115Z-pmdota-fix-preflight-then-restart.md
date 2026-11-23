# To IT, 23 Nov 2026 11:15Z: pmdota recorder fix. Run the pre-flight now; restart ONLY if it passes AND the approval row is cleared (see INBOX NEEDS-NICK P-DOTA-6)

Cause (P111 thanks): Polymarket moved the start of Team Synapse v InterActive Philippines (first listed 19 Nov); the old recorder cached the first start, so its window never reopened and books.jsonl stayed empty in the live game. Fixed in default branch 353787e35f (PRs 468, 469): start re-read each discovery, paging past 100 events, single-instance lock, token log, prompt stop. Tests committed (feeds/test_pm_dota_books.js ALL PASS; old code FAILS it).

STEP 1 (read-only, any time, seconds of work, do first): from a clean export of default branch tip 353787e35f or later run
`bash feeds/preflight_pmdota.sh 75`
It writes to a scratch dir only. Paste the whole output to dialogue/from_agent/pkarbs/P-pmdota-preflight.md. Exit 0 = PASS, 1 = FAIL, 2 = UNVERIFIED (no market in window). The 13:00Z game (potn9ki v Team Synapse) makes the data check testable from 12:40Z to ~18:00Z; run it inside that window.

STEP 2 (only after STEP 1 exit 0 AND the NEEDS-NICK row is cleared or its stated default time has passed; BLAST games 14:00Z and 17:00Z today, so best done by 13:30Z):
a) copy feeds/pm_dota_books.js from the export to /mnt/HC_Volume_107257520/pkarbs/pmdota/pm_dota_books.js (keep the old one as pm_dota_books.js.old);
b) stop old pid (SIGTERM; old code only ends after its 5-minute discovery sleep, it writes no books after the first 2 s; kill -9 after 10 s is fine, it keeps no state); KEEP ALL FILES;
c) start the new copy with EXACTLY the old command line (same node path, same dir, same end date 2026-12-02T00:00:00Z as your ps line of pid 2539785 showed), single instance.
STEP 3: HEALTH READ within 15 min of the start (R-037): `bash feeds/check_pmdota.sh /mnt/HC_Volume_107257520/pkarbs/pmdota` (one node pid), `tail -5 recorder.log` must show 'discovery markets N tokens 2N' with N>0, books.jsonl size growing 60 s apart during a live game, and `df -h`. Any fail: stop it, keep files, tell me, no retry.
