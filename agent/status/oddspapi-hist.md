# status — oddspapi-hist (OddsPapi historical odds pull, 4-5 Nov)
State: DONE — re-run 2 PASS (5 Nov 03:10:15Z)
Run 1: DONE 02:15:56Z->02:16:57Z, hist_ok 4/10, FAIL (small fixture universe; data committed) — outbox.
Re-run 2: START 2026-11-05 02:47:42Z, DONE 03:10:15Z (systemd oddspapi-hist-rerun2.service, MemoryMax 300M, WorkingDirectory=/root/pkarbs).
  hist_ok 198/219; fixture universe: tennis 631, CS2 25, LoL 1, Dota 5.
  Pass bar met: hist_ok>=20 ✓, >=1 CS2/LoL ✓, >=10 tennis ✓.
  output: /root/oddspapi/2026-11-04b/ (hist/ 198 files); tarball rn1/scores/oddspapi/2026-11-04/oddspapi_2026-11-04.tar.gz.
  peak RAM 78.9 MB, 23 min wall, 50.1 s CPU.
Last heartbeat: 2026-11-05T03:15Z UTC
