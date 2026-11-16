# URGENT to IT: PandaScore raw hours 12:00Z-15:00Z unreadable or missing (16 Nov 20:20Z)

Source: agent/outbox/TO-IT-pandascore-post-restart-readback-2026-11-16.md. Good news first: the 4004 fix works (0 close errors since 12:25:21Z; 17 sockets started and connected; 12 normal 1000 closes). The problem is raw data. One chunked task, read-only first, due 14 hours before BLAST day ends, i.e. 17 Nov 08:00Z at the latest.

1. **Missing hours 13:00-15:00Z.** Before calling them lost, check the box copy `<box>` pkarbs/pandascore/raw/ and ship.log. The shipper deletes the local file after a successful ship (see the P7 note), so absent locally may mean shipped. Report which hours exist on the box and which exist nowhere.
2. **12:00Z file fails `gzip -t` (invalid compressed data).** The restart at 12:25:21Z cut the append-streamed file. Please read it tolerantly and report how many rows from 12:00-12:25Z (old process) and 12:25-13:00Z (new process) are recoverable. This is the same BADGZ class as hour 22 on 13 Nov, still open: propose the tolerant-reader fix for `ship_raw.sh` for the next approval.
3. **Reconcile the analysis directory.** The PandaScore lead-test runs (ps-lead-test-2026-11-15.md, ps-lead-audit-2026-11-16.md) count 14.8%, 7.5%, 8.2%, 10.5%, 13.2% fewer events than the 14 Nov recount (rounds, kills, towers, barracks, Roshan) from the same 23 matches. Missing or unreadable hours in the analysis directory would explain that. Say which hours each of the two runs read, and whether the full 13-16 Nov set is complete anywhere.
4. Before BLAST (17 Nov): confirm the next restart or hour rollover cannot truncate an open hour file again, or say what a safe procedure is.

Count only. Cite feeds/STANDARD-feed-latency-test.md; no lead or verdict.
