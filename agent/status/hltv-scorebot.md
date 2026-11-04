# Status: hltv-scorebot — Run 1 STOPPED (per reviewer drop-note 13:18Z); data preserved

**State:** STOPPED — pid 798702 (relaunch 14:19Z) killed 2026-11-04T15:47Z. No `capture.js config-run1` process remains (`ps`/cmdline scan clean). Reconciliation stamp 2026-11-04T15:47Z.
**Why stopped:** reviewer drop-note `agent/inbox/2026-11-04-drop-hltv-run1-and-crossbet.md` (13:18Z) ordered run 1 NOT run on the server (it runs on Nick's own machine): "Do not start it on the server. If you already started it, stop it." A session relaunched pid 798702 at 14:19Z after the note; that contradicted the note and has been stopped again. This is the reviewer's in-repo instruction being carried out, not a new action.
**Pass already met:** >=50 `"ev":"log"` Kill rows for match 2400076 (13:00Z), captured before the 13:36 death — confirmed in earlier status 15:08Z.
**Data preserved:** /root/hltvcap/run1-2026-11-04 (891 MB; scorebot.js jsonl + books from 12:18–13:36Z) left on disk. Copy of it was already pushed to `live/cs2_feeds/raw/hltv-2026-11-04/` on thread 6tydow (bc087169).
**Run 2 (IEM playoffs 6 Nov):** NOT started, awaiting a new approval note per the drop-note.
**Errors:** none. **waiting for Nick:** none new — run1 stoppage per reviewer drop-note; Run 2 waits on its own note.
