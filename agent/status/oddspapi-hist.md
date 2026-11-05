# status — oddspapi-hist (OddsPapi historical odds pull, 4-5 Nov)
State: RUNNING — re-run 2 (5 Nov 02:35Z note: keep finished fixtures, skip table tennis, esports first)
Run 1: DONE 02:15:56Z->02:16:57Z, hist_ok 4/10, FAIL (data committed) — see outbox.
Re-run 2: START 2026-11-05 02:47:42Z, unit oddspapi-hist-rerun2.service (MemoryMax 300M, WorkingDirectory=/root/pkarbs)
  output: /root/oddspapi/2026-11-04b/ (fixtures_tennis 631, cs 25, dota 5; hist/ growing)
  progress: 20/219 hist calls ~02:49Z, 30 hist rows written, remaining 404s = fixtures with no odds in window
  ETA ~25 min (5.3 s cooldown between hist calls). Completion outbox posted by next dispatch round.
  Pass bar: hist_ok>=20 AND >=1 CS2/LoL AND >=10 tennis. Runs at most 3600 s.
Last heartbeat: 2026-11-05T02:50Z UTC
