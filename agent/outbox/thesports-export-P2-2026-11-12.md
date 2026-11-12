# thesports-export-P2-2026-11-12

OPEN row P2: TheSports export (incl. Dota) was stranded since 12:34Z. Cause: every 2h-timer build takes ~50-75 min, and the 15-min dispatch advances `claude/project-thread-vg2ckg` during the build, so the push at the end is non-fast-forward-rejected. This is a race against the dispatch, not a CB15 defect (CB15 narrowed the window; it did not remove it).

## Fixed (2026-11-12 ~14:59Z)
- Replayed the rejected 14:51Z build (commit db86400a, +22,277 slim files) onto the current origin tip using a batch index-info tree (mode-sha1-TAB-path) and a single push — the push window shrank from minutes to milliseconds, so it landed.
- **Commit on origin: `b0f427ff`** (`refs/heads/claude/project-thread-vg2ckg`)
- Files added: 22,277 (all under `rn1/scores/thesports/final-topics-32295b-slim/`)
- H-compliant: 0 non-slim changes vs parent (grep count = 0). Nothing removed outside the slim paths.
- Newest data on origin now: ts_mqtt minute `1794488400000` = **13:00Z**, books_mid to 13:15Z.

## Cause of the stall (measured)
- 13:16:06Z attempt: `a914f9e` +17,923 files -> push_rc=1 (non-fast-forward)
- 14:51:12Z attempt: `db86400a` +22,277 files -> push_rc=1 (non-fast-forward)
- Both builds finished after the branch had advanced past their base tip; the single-retry-on-fresh-tip in the timer script does not rebuild-and-repush the finished files onto the newest tip.

## Remaining
- The 13:00Z->now tail is being closed by a background exporter run (recomputes SINCE from the now-13:00Z origin tip); its push should land the same way.

## Revert
- None needed (additive export push). The files are the export's own output and are the intended delivery.
