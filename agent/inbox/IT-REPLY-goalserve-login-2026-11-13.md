# IT reply: Goalserve login (13 Nov 2026, 02:10Z)

Your TO-IT line (TO-IT-goalserve-missing-login-2026-11-12.md, 2461a86) is routed to trading-test `dialogue/OPEN.md` row **P3**, which runs after the temperature and MFW rows. OPEN row P1 is updated: key installed, IP match yes, inplay feed loads yes.

P3 asks the agent to:
1. Find the Goalserve login in the same message where Nick gave the key (about 13:11Z; CHANGE-BATCH #18 covers both). Add it to `/etc/pkarbs/goalserve.env` and never print, log or commit it. Then rerun gettoken.
2. Before that, check the gettoken request against the Goalserve docs and say in one line whether the 400 comes from the request format or the missing login.
3. If the login is in no session, write that in the TO-IT file. It stays under CHANGE-BATCH #18 and does not become a new item.

Done when agent/status/goalserve.md shows WS token yes/no and gives a pkarbs commit SHA.
