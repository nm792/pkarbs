# Cricket separate capture — STARTED 04:05:18Z 2026-11-10

RESULT: independent cricket-only capture is live, capture-b untouched.

- Started: 04:05:18Z (launch ms 1794283518595), 48 h window, unit `thesports-capture-cricket` via start_writer.sh + systemd-run --scope, MemoryMax 650M, MemorySwapMax 0.
- Output: /vol2 .../pkarbs/thesports-cricket/2026-11-10 (log.jsonl, pmws.jsonl, ts_mqtt.jsonl, ts_poll.jsonl), `--no-books` as instructed.
- Topics: env override THESPORTS_TOPICS=thesports/cricket/match/v1 only; connect rc=Success; **mqtt_suback: Granted QoS 0**.
- Message counts at ~10 min (04:15Z): ts_mqtt.jsonl 38 rows, pmws.jsonl 89 rows. **A cricket match is live now** — ts_mqtt carries match id zp5rzpcdx6n4q82, batting runs 281 / balls faced 408 (real match data flowing, so messages are expected).
- Single-instance guard: flock on /run/writer-locks/<unit>.lock **per unit name**, not global — cricket holds its own lock, capture-b (pid 2818605) holds its own; both coexist, capture-b untouched.
- Disk: /vol2 before launch 16 G free (floor 15 G) — passed the charter check at start; cricket writes are small.
- Export: 2 h export currently covers only final-topics-32295b (capture-b). The cricket ts_mqtt export needs the export script extended — **approval item raised** (class-4 code change), see APPROVALS. One-off cricket export pending that.
- No /etc edits, no env file copied, no secrets in git, no orders placed, deleted nothing.

Count: notes run 1, outstanding 0, PENDING open 1 (export script extension).
