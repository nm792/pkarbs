# IT 05:22Z 20 Nov: three idle PK arbs folders ship to the box (T0k5)

Goal: get VOL2 well clear of its 10 GB floor so your live recorders keep running.

Position: VOL2 had 11.2 GB free at 05:04Z, falling about 0.5 GB/h (dialogue status/T0k4-vol2-map.md, 10b79ff3). final-topics-32295b is live book data and stays put.

The one item: the temperature job's next session (T0k5) copies these to the box under prime/vol2-archive/ with the same paths, verifies the checksums, then deletes only the verified local copies:
- pkarbs/from-vol: 6.8 GB, last written 17 Nov, nothing holds it open.
- pkarbs-ps-step2: 3.4 GB, last written 16 Nov, nothing holds it open.
- pkarbs/scratch: only files older than 2 days, skipping anything held open.

Nothing is lost: IT copies any of it back on request. If you need any of these on local disk, reply here before the next temperature session (about 05:30Z) and IT will pull that folder from the row.
