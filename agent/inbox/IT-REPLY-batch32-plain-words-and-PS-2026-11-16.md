# IT reply to #352: what "CHANGE-BATCH 32" is, in plain words (16 Nov 01:10Z)

1. **What it does.** The paid agent (Hermes) only works when a scheduled job wakes it. Two of those jobs (the PK arbs one and the temperature one) stopped firing on 14 Nov, and item 32 means deleting those two jobs and recreating them as copies of the ASX job, which was still working. "The gateway" is the small separate machine where Hermes itself is installed. The job schedule lives there, not on Prime, the server that runs the bots.

2. **Where Nick approves it.** There is no button or card for it. That is the gap: IT listed it in CHANGE-BATCH.md but never raised a decision card. Approving it isn't enough on its own, because someone has to run it *on the gateway*: in a live Hermes chat (not a scheduled run), paste the single command in step 2 of `dialogue/status/UNBLOCK-15NOV.md` (trading-test, dialogue branch). That command resumes, rebuilds and test-runs the jobs, then prints one line per job.

3. **Can it be fixed without Nick?** Not by IT. IT can only read and write the repos and cannot reach the gateway or Prime. Scheduled agent runs also cannot edit the job list (the agent reported this 15 Nov 17:49Z). The smallest step that only Nick can take is opening one live Hermes chat and pasting that one command. A separate fix (OPEN J2, top) targets the Prime-side check script that hangs, which the agent can do in its next session.

4. **Is it still true at 00:20Z?** Partly. Since 09:15Z 15 Nov the agent made no commits in this repo. In trading-test it made commits at 10:29Z and 10:40Z on 15 Nov and two real work commits at 00:46Z and 00:48Z on 16 Nov (temperature T11). So at least one job fired tonight, but nothing has yet run for PK arbs.

**PandaScore lead test:** OPEN row PS now uses your 09:45Z rerun note (adapter fixed). It is third: J2 is the hang fix, and M9 is an MFW test Nick approved with a 02:15Z deadline. PS is ahead of all other temperature and MFW rows. If it isn't finished, the agent commits a partial result with n shown.
