# IT-OPS STANDING RULE 2026-11-22 07:16Z: 15-minute health read for EVERY recorder or paper run (REPEAT)

Owner: IT (Hermes) and every project. Source: Nick 07:15Z 22 Nov, after T45 ran with 17% HTTP 429 and nobody checked it until he asked (only about 11% of hours fully recorded, so the run could not judge fills). This is a REPEAT failure of the 15-minute sanity rule.

**Rule, for every recorder or paper run in every project (Temperature, MFW, PK arbs, Webb, ASX):**
Within the first 15 minutes of a start or restart, post a HEALTH READ in the run's status cell or status file:
1. Snapshots captured vs expected (count and %). **Pass bar: >= 99%.**
2. Unhandled errors (HTTP 4xx/5xx, exceptions, empty books). **Pass bar: 0** (errors that are retried and recovered count as handled; report them).
3. Prices come from the traded token's **own** book (name the field or line that proves it). **Pass bar: yes.**
4. Disk free on the output volume, and the pid.

**If any bar fails:** stop the run, keep its files, fix it, and restart. The health read for the restart is due within 15 minutes of that restart. Write FAIL and what it means for the test in plain English. The Reviewer tells the coordinator at once.

**Applies now to:** Temperature T45 v2 restart (IT-OPS-2026-11-22-0713Z), PK NBA and CS2 recorders, the MFW box recorder (M43e) and forward runner, and every new run from here on.
