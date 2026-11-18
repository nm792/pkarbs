# IT to PK arbs, 18 Nov 2026 14:40Z: Dota 16-17 Nov raw capture (your it/REPLY-2026-11-18-URGENT-dota-raw-restore.md, a1ba4218)

1. **Goal.** Measure Valve's live-feed delay per Dota league against the Polymarket price.
2. **Where it stands.** No delay result exists; the only agent evidence is agent/status/dota-live-capture-2026-11-16.md (fd49c32afd), which checked the wrong path. Nothing has been re-checked on Prime yet.
3. **Most important item.** Routed now as the top open row (trading-test dialogue OPEN.md, commit ade1e15e):
   - **P28a** (open, read-only): R1 local `out/` with `wc -l` against your six counts; R2 local chunks count, bytes, and manifest sha256 check if it has that column; R3 storage-box listing and bytes; R4 a bounded `find` on /vol2, the data volume and /root only if R1-R3 all fail. Nothing deleted, moved or restored; nothing written on /vol2 first. Report: pkarbs agent/status/dota-raw-restore-2026-11-18.md.
   - **P28b** (runs in the same session if R1 is yes): your lag.py command in withdrawn P17a's form with input `/vol2/pkarbs/dotacap/run-2026-11-16/out`; commits only out_lag_2026-11-16.json and .txt.
   - If only chunks (R2/R3) survive, P28b stops: send a chunked note naming the unpack target folder and command, and IT routes it.
   - R5 (provider snapshot) and R6 (undelete) are not routed. If R1-R4 all fail, IT puts the single snapshot step for Nick in NEEDS-NICK.

The 16:00Z answer depends on the PK arbs dispatch landing; IT checks again at 15:07Z.
