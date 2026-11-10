# TheSports cricket separate capture — LIVE 2026-11-10 (reply to inbox note)

## APPROVALS NEEDED:
- CHANGE-BATCH round 2026-11-10 item #6: add cricket ts_mqtt rows to the 2h slim export (edit the export timer topic list). Not applied; awaits Nick's approval line.

## RESULT
1. Cricket-only capture LIVE: started 04:05:18Z 2026-11-10, 48 h window, `--no-books`, OUT /mnt/HC_Volume_107257520/pkarbs/thesports-cricket/2026-11-10, launched via start_writer.sh + systemd-run --scope --unit=thesports-capture-cricket (MemoryMax 650M, MemorySwapMax 0). capture-b (pid 2818605) untouched, still running.
2. Topics: THESPORTS_TOPICS=thesports/cricket/match/v1 passed inline; all other variables read from /etc/pkarbs/thesports.env (read-only; no secrets in git). mqtt_suback: Granted QoS 0 (log.jsonl).
3. Message counts: ~10 min (04:15Z): ts_mqtt 38, pmws 89. ~45 min (04:50Z): ts_mqtt 232, pmws 421. 1-h check due ~05:05Z.
4. A cricket match IS live now — ts_mqtt carries match id zp5rzpcdx6n4q82 (inning 1, overs/timeline flowing), so messages are expected.
5. Single-instance guard: flock on /run/writer-locks/<unit>.lock is per unit name, NOT global — cricket holds its own, capture-b holds its own; both coexist (ps: cricket 1829238, capture-b 2818605).
6. Disk: thesports volume passed the charter floor at launch; cricket writes small (~4.8 MB in 45 min).
7. Export: 2h slim export covers only final-topics-32295b (capture-b); cricket ts_mqtt excluded until CHANGE-BATCH #6 lands. One-off cricket export pending that.

## DATA
- OUT: /mnt/HC_Volume_107257520/pkarbs/thesports-cricket/2026-11-10 (log.jsonl, pmws.jsonl, ts_mqtt.jsonl, ts_poll.jsonl)
- Live procs: 1829237/1829238 (cricket), 2818604/2818605 (capture-b)

## OPEN / NOT VERIFIED
- 1-h message count (due ~05:05Z) not yet measured.

Count: notes run 1, outstanding 0, PENDING open 1 (CHANGE-BATCH #6).
