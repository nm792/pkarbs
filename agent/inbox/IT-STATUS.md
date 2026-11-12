# IT status for PK arbs (IT updates this at every check). Last updated 12 Nov 2026 01:50Z.

**Done**
- CB15 push-race fix applied at 19:26Z (de0517c84).
- The thread tree was restored after the agent's 7dbd4fb run deleted tracked files (20:14Z).
- Mention-books recorder running.

**Open, near the top of the agent queue (trading-test dialogue/OPEN.md)**
- Row E: the TheSports hand export said "in progress, push will land" at 23:40Z and nothing has landed. The agent must finish the push or report the failure, and confirm that the next timed 2h export lands.
- Row D: VOL2 is at 7.7 GB free, under the 15 GB floor. The agent checks that both captures ship hourly to the box and delete locally, ships any verified backlog, gets VOL2 above 15 GB, and adds VOL2 to your heartbeat.

**How it works**
- The agent wakes every 30 minutes while anything is open.
- IT has found that the wake check was not scanning every project inbox, and that is being fixed (OPEN row B).
- Your yes is the approval for PK arbs changes.
- Escalate to trading-test `dialogue/TO-IT.md` any inbox item unanswered for more than 60 minutes.
