# IT reply: 13 Nov (12:40Z)

**I'm sorry: IT caused today's wipe.** Commit 7fb0b1ce0 at 06:11Z, which deleted 372,920 files from this branch, came from IT's own scheduled check. It wrote its reply from a partial (sparse) clone, so the commit dropped everything outside it. Thank you for restoring the tree in #294. Fixed: the IT check may no longer clone, commit or push in this repo, and it checks for deletions before any push.

**Why nothing has moved for 6 hours:** the agent queue had temperature and MFW at the top (Nick set those two as equal top priority), and PK arbs never reached the top. That has been changed. Your row P4 (#289, #290, #292, then the TASK files oldest first) is now the top actionable row. The IT check also now keeps at least one PK arbs row in the top 8.

**Status:** the TheSports export landed at 10:45Z (+31,908 files). Goalserve (P3) is still blocked on the WS token login.
