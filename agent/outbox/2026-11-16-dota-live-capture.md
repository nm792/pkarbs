# Dota 2 live capture — 16–17 Nov (update 12:03Z)

- Capture remains active: timeout PID 1700947 and Node PID 1700948; both were running at 12:02:51Z, with output advancing through that time. At 12:02Z observed rows: books 13,485; capture.log 2,694; league_games 2,442; opendota_live 421; realtime 19,674; rt_polls 46,056; sportsws 785.
- The scheduled and manual publisher attempts since the 11:04Z verified push continue failing before transfer: rsync exit 255, storage-box authentication rejected. No new remote manifest was pushed; publisher state remains at 11:04Z and nine complete local chunks are retained. No publisher offset was advanced for failed transfers. Latest verified remote manifest remains commit `27f7b9ee0bedc5d8f8613b154a318c3d0327ba8e`.
- Capture, publisher code, configuration, crontab and credentials were not changed. I did not read or modify credential values. The capture continues through 17 Nov 20:30Z; final coverage/pass-fail remains unmeasured.

## Next required action / safety

- The only blocker is storage-box authentication for the already-installed publisher. Until authentication works, new output remains local and the remote copy is stale. Existing chunks and source output are retained; no offset was advanced past failed transfers.
- Revert is not applicable; no code or configuration was changed.
