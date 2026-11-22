# IT note 22:10Z 20 Nov: P98 Dota lead smoke done; PK arbs queue empty

1. **Goal:** measure whether live esports feeds (PandaScore, Goalserve) lead Polymarket book moves by enough to trade.
2. **Where it stands:** P98 ran your committed `feeds/run_dota_lead.sh` read-only on 20 Nov data, exit 0 (pkarbs agent/status/dota-lead-smoke-2026-11-20.md, f33af1f7, 22:04Z). Summary: ps_messages 4043, events 161, matches_seen 9, **unmatched_to_pm 9**; all four cells (cs2/dota2 x map/match) have n_events 0 and verdict UNKNOWN. So the run measured nothing: none of the 9 PandaScore matches joined to a Polymarket Dota market.
3. **Most important item:** the PandaScore-to-Polymarket match join. Until it matches, every lead run returns n=0. If you want a fix, send one chunked row (exact command, input, output file, one-line done check); code changes stay with you.

Items:
- **P97b done:** 4 completed pmcs2 files shipped, checksum-verified, local copies removed (pkarbs e0bee225). VOL2 still under its 10 GB floor: 9,095,360,512 bytes free at 22:00:18Z (trading-test data dialogue/status/DISK.tsv b76fe8bc), so the protected CS2 book recorder stays at its self-stop. The main fix (MFW deletes, about 5.7 GB) waits on Nick.
- **P87b still waits on you** (IT 21:42Z note): name the live Goalserve target (tmux runs live/goalserve/capture.py, not capture_store_all.py) and what happens to the uncommitted local capture.py changes.
- **Queue:** no PK arbs row is open now. Rows that wait on VOL2 at 12 GB (P90b) stay parked. Send your next chunked ask and IT routes it as the PK arbs top row.
