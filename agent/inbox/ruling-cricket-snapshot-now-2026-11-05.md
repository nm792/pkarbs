# Addendum to ruling-root-disk-and-tennis-restart-2026-11-05: cricket-feeds snapshot

From the project thread, 12:45Z 5 Nov. The cricket thread has asked three times (latest nudge 3, commit 7c88e1d4) and your last cricket snapshot was 09:01Z (e46a270). Status says RUNNING, so something stopped the hourly share commit.

Do now, before the other disk work:
1. **Commit a cricket-feeds snapshot** of /root/cricket-feeds/2026-11-05 to rn1/scores/cricket/feeds-2026-11-05/ (gzip -t each file; split anything over 90 MB). Do NOT stop or restart the capture. Copy, don't move.
2. **If you can't, say exactly why** in agent/outbox/2026-11-05-cricket-feeds.md (disk full on `/`, git push failing, file size over the GitHub limit, memory cap, or the round simply skipped it). Include `ls -la` of the dir, `df -h /`, and the last error.
3. Keep the hourly commit going. After each committed snapshot, delete only the raw already committed AND gzip-verified, as in the tennis rule, so the cricket dir stops growing on `/`. The raw books file was 110 MB at 09:01Z and is now much larger; that is probably what blocked the single-file commit.
4. Put the cricket dir size in the root disk breakdown. The capture ends ~17:15Z.

Reply in the existing cricket outbox file. Never commit keys.
