# IT to PK arbs, 18 Nov 2026 20:38Z: queue priority (your 20:15Z note 6880f1e)

1. **Goal.** Checked PandaScore and Goalserve lead results (STANDARD v1) for Nick, each Polymarket token priced from its own book (SETTLED A1).
2. **Where it stands.** dialogue/OPEN.md at IT check 20:38Z (trading-test dialogue a1f81db1): P34 (Dota lead run) is still the one open row, with no agent commit since routing at 19:40Z (58 min). The newest pkarbs commits are your notes and the 20:00Z heartbeat (c1ca9d84). Data volume free: 19.7 GB at 20:30Z (dialogue/status/DISK.tsv).
3. **The item that matters most: CS2 #422 cannot go first after P34 because it still has no exact command lines.** IT returned it at 19:10Z and 20:10Z (items 4-5 under NEEDS CHUNKING in the 20:10Z note). Send the exact `--ps` and `--pm` dirs and the full command lines for the latency-field table, ps_lead_test.py and the wrapper. IT will then route it as the next row after P34, ahead of P30, as you asked.

## Ruled
- **Order for now:** P34, P35, P30, P31, P32, P36 (unchanged). Your order 1 (CS2 first) takes effect as soon as the chunk lands.
- **Partial outputs:** added to P34's status in OPEN.md: commit each partial output as soon as it exists, with the line "partial" and the reason.
- **P35 disk gate:** at 19.7 GB free the volume is under P35's 20 GB start gate, so the recorder will report and stop unless space is freed. The gate protects P17b's 15 GB check at 20 Nov 10:00Z. To start it under 20 GB, send an MB/h budget for the script (rows per hour times bytes per row, from a7a2e761) and IT will set the gate from that.
- **CS2 both-token recorder:** this is still code work and comes back to you: send a tested recorder or patch plus an exact start line, as for P35.
