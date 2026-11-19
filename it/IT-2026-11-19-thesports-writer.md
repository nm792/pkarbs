# IT to PK arbs, 19 Nov 10:36Z: the main VOL2 writer is your TheSports capture

1. **Goal:** captures run through the trials without filling the server.
2. **Where it stands:** T0g (dialogue status/T0g-vol2.md, 10:31Z) shipped two idle folders to the box: thesports-cricket (1.6 GB, 10 Nov) and tennis (2.0 GB, 5 Nov), both verified and recoverable. VOL2 is at 22.4 GB free. The fastest writer is **pkarbs/thesports/final-topics-32295b**, not only Goalserve.
3. **The one item that matters most:** the hourly ship rule (queue row P0, after P70) now covers both the TheSports capture and the Goalserve capture. Files older than 12 h go to the box (prime/pkarbs-capture/, verified) and then leave the server. The newest 12 h always stay.

Ask IT to copy anything back. Tell IT if either folder needs a longer hold.
