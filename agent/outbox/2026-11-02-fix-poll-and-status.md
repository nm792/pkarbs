# Outbox: fix-poll-and-status done (2 Nov 2026)

Both gaps fixed.

1. Rugbyrama 15 s widget poll added to capture.py as the fourth async task (`poll_rugbyrama`). It polls `https://www.rugbyrama.fr/idalgo/cache/page/rugby_widget_match.php?refMatch=<id>` every 15 s with the honest UA `pkarbs-research/1.0`, writes one line per poll to `rugby/<win>_rugbyrama.jsonl` (time, refMatch, status, size, score, body) and first-seen event rows to `rugby/<win>_rugbyrama_events.jsonl`. Window->match-id map: AB=[61243,61242,61237,61239,61240,61241], D=[61243], C=[61238]. Failure rule: 3 consecutive errors on one match -> that match's clock marked FAILED (report only), does not fail window gates. No change to existing gates.
   - Local test (protocol rule 1) run before committing: `_parse_rugbyrama` on the live 61242 widget (HTTP 200, score `0 - 0`, 1 comment parsed); synthetic 2nd-event page -> first-seen dedupes (page-1 event logged once, page-2 event logged when first seen); error path -> consec_fail reaches 3 + `RR 61242 FAILED` written. `shadow/test_gates.py` = 25 of 25 gates pass; `py_compile` clean.
   - Commit: see `git log --oneline -1` (hash in the round summary below if needed).

2. Status corrected. Harness line now `timeout 18000, nice -n 19` (not 10500). capture.py `run_for` made window-aware (AB=18000s per Nick's 15:50Z run-longer approval; D/C stay 10500s), so the 5h AB window is not truncated by the old 10500s self-cap; "Next" line now `run window AB 7 Nov 13:15-18:05Z, then D, then C, one at a time`. Rugbyrama outputs added to the Outputs line.

Status file updated + both this reply and the nick-approvals acknowledgement pushed (see round commit).
