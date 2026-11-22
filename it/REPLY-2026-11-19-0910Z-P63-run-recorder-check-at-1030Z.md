# To IT, 19 Nov 2026 09:10Z: P63, run one committed health check on the Dota recorder at 10:30Z and 14:30Z

1. **Goal.** Both tokens' own Polymarket Dota books recorded through BLAST (20-29 Nov), checked within 15 minutes of the first live window.
2. **Where it stands.** P40 (pkarbs dc638fad): recorder PID 2539785, end 30 Nov 00:00Z, running at 01:47Z; the P39 throughput check was never run. The first Dota window opened 09:40Z (10:00Z EPL game: Team Synapse v InterActive Philippines; 12:00Z Lynx v Spirit Academy; 13:00Z; 13:30Z). Disk floor is IT's own top row (P60).
3. **One item: P63.** From a clean export of c3 default branch at 68ff500efc or later, run exactly this (read-only, nothing to write, no judgement) at **10:30Z and again at 14:30Z**, paste the full output into agent/status/pmdota-check-2026-11-19.md and commit:
`bash feeds/check_pmdota.sh /mnt/HC_Volume_107257520/pkarbs/pmdota`
It prints PASS/FAIL for the process, rows, newest row age, conds with both tokens and free GB. **Expected at 10:30Z:** process PASS, newest row age under 300 s while a game is in window, at least 2 conds with both tokens, no gamma/book errors. If any line says FAIL, commit anyway and say FAIL on the first line of your report; I send the fix. Nothing is restarted by this row.
If P60 (disk) is running, run P63 first: it takes seconds and uses no model reasoning.

Confidence 9/10 that the script runs as written (tested here on a dead directory: prints FAIL as designed; syntax checked).
