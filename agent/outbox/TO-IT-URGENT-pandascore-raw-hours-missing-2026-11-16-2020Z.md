# PandaScore raw-hours check — 16 Nov 2026 (step 1 of 4)

Scope: step 1 only, per the OPEN row's one-step-per-session instruction. Read-only; no data or process changed.

- Box copy verified for 13:00Z: `pandascore_2026111613.jsonl.gz`, 222,224 bytes, 1,676 rows.
- Box copy verified for 14:00Z: `pandascore_2026111614.jsonl.gz`, 307,704 bytes, 2,277 rows.
- Box copy verified for 15:00Z: `pandascore_2026111615.jsonl.gz`, 289,288 bytes, 2,336 rows.
- Each file was read from the box, passed `gzip -t`, and decompressed to the stated line count. The box directory listing confirms all three names.
- The local originals are absent; `/root/ship/manifest/manifest.tsv` records each as `box` / `deleted` at 15:30:39Z, 16:30:41Z, and 17:31:22Z respectively. Thus none of hours 13–15 is missing; all are present on the box.

Data/evidence: Prime read-only box checks and `/root/ship/manifest/manifest.tsv`; no evidence file copied or changed.

Remaining steps not run in this session: (2) tolerant-read the 12:00Z file and propose the shipper fix; (3) reconcile both lead-test input sets; (4) state safe restart/rollover procedure.
