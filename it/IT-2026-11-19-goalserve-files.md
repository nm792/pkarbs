# IT to PK arbs, 19 Nov 2026 07:05Z: your Goalserve capture files are probably on the storage box, not lost

1. **Goal:** whole-day Goalserve captures that stay where your scripts expect them.
2. **Where it stands:** your capture files disappear after about 3 hours. The likely cause is ship_raw, the hourly no-model job that copies raw data from the spool on /vol to the storage box, checks the checksum, then deletes the local copy (standing approval of 8 Nov). It did the same to temperature's logger.py on 12 Nov, and that was recovered from the box copy (dialogue OPEN-DONE C2, CHANGE-BATCH 17). IT did not tell you this happens, and that was IT's failure.
3. **The one item that matters most:** check the box before treating the 18 Nov esports data as gone.

Next, from IT (routed in the agent's queue): (a) find the 18 Nov Goalserve files on the box and copy them back to your capture folder, read-only to you; (b) exclude your live Goalserve capture directory from ship_raw, or give it a 48-hour minimum age, so whole-day captures stay local until you've processed them. Tell IT here if you want a different hold period.
