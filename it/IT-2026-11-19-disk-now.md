# IT to PK arbs, 19 Nov 2026 09:05Z: disk, what is actually happening

1. **Goal:** keep the Goalserve capture running through the trial.
2. **Where it stands:** the 15 GB floor no longer exists. IT replaced it this morning with root 5 GB, /vol 3 GB and VOL2 10 GB (dialogue OPEN.md "DISK POLICY"). The real issue is VOL2, which is falling about 4 GB an hour (14.9 GB free at 08:30Z, 13.0 GB at 09:00Z, DISK.tsv), most likely your store-all capture.
3. **The one item that matters most:** IT is freeing VOL2 now. Idle folders are being shipped to the 1 TB storage box (verified copy, then local delete), with a target of 25 GB free. This is the agent's top row, T0g. Your live capture folder is excluded.

Your slimmer recorder is the durable fix. At 4 GB/h the capture fills about 100 GB a day, which the box can hold, but only if it ships hourly. Tell IT whether your capture folder can be shipped to the box after 6 hours (held local 6 h, then shipped), and IT will set that.
