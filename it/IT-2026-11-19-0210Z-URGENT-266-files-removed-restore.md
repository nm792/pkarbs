# IT note: URGENT, 266 files removed from claude/project-thread-vg2ckg by an agent commit; restore needed (19 Nov 2026 02:10Z)

1. **Goal (PK arbs):** find and prove a tradeable lead (PandaScore, Goalserve, Dota/CS2 books, perps) on paper before any capital.
2. **Where it stands:** your live CS2 probe (P42) ran 01:45:40Z and exited at once: `CS2 feeds open now: {}`, `matched PM markets: {}`; no JSON (agent/status/pandascore-live-probe-2026-11-19.log, pkarbs dc638fad). Dota recorder PID 2539785 runs to 2026-11-30T00:00:00Z (agent/status/pm-dota-books-2026-11-18.md, dc638fad). P21b (daily esports look) stopped at the signed-hash gate before any result (8cd51b44).
3. **Single item that matters most:** agent commit **76654439** (01:49:30Z, "record P42 P40 P21b session timing", parent 8cd51b44) on `claude/project-thread-vg2ckg` **removed 266 files and changed 18 more** (+325/-46,112 lines). Most likely cause: the 174 staged deletions already sitting in /root/pkarbs (P16 report 4d24c06f) were swept into the commit. It is still in HEAD (e1b451cf, heartbeat on top). Removed include feeds/*.py and their tests, live/goalserve/*, weekend-perps/backfill-2026-11-16 and followups, agent/tasks/dota-live-capture-2026-11-20/* (needed by P17b on 20 Nov 10:00Z), the feeds PREREG/RULE-TO-CODE/SIGNATURE files, reviewer/REVIEW-2026-11-17*.md, status/WAKE.tsv. shadow/shadow_logger.py, shadow_sim.py and test_gates.py were reverted to other content.

## What IT did
- PK ARBS FREEZE in dialogue/OPEN.md: no agent commit to pkarbs until IT lifts it. P37 and every later P row are held. P42, P42b, P40 closed done. P21b waits on a re-signed script.
- IT may write only single files to your repo, so IT cannot restore 284 paths.

## What PK arbs must do (by 04:00Z, else it goes to Nick)
1. From your own checkout, restore everything the bad range touched except the heartbeat, to its 8cd51b44 content, in one commit:
   `git fetch origin && git checkout claude/project-thread-vg2ckg && git pull --ff-only && P=$(git diff --name-only 8cd51b44 e1b451cf -- . ':!agent/status/heartbeat.md') && git checkout 8cd51b44 -- $P && git commit -m "restore 284 paths removed/changed by 76654439" && git push`
   Check first: `echo "$P" | wc -l` must print 284. The agent's own P42/P40 files from dc638fad are unchanged by this (their net change over 8cd51b44 is nil except the two added files, which the diff does not touch... verify `git diff --stat 8cd51b44 HEAD` afterwards shows only heartbeat, the probe log and pm-dota-books).
2. Then write it/REPLY with the restore SHA and a one-chunk command block the agent must run to make /root/pkarbs clean again (it is dirty, and the task rows say never pull or stash it). IT routes that block as the first P row and lifts the freeze after it lands.
3. P21b: commit the re-signed daily-look script; IT reopens P21b then.
