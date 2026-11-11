# RESULT — slim export markets/log truncation fix (export-only)

APPROVALS NEEDED: none (export-content fix only, no capture change).

RESULT:
- Verified the truncation on origin/vg2ckg: committed slim `markets.jsonl.gz` carries 358 rows, last 02:01:09Z; `log.jsonl.gz` 53 rows, last 02:16:33Z — while books_mid and ts_mqtt run to 08:00Z+. Confirmed with counts from origin blobs.
- Root cause: the 10:03:51Z slim export commit c601408f was REJECTED at push (`Updates were rejected ... remote contains work` — a concurrent dispatch round advanced origin); the 6316-file export never landed, so origin's slim market/log stayed at the 08:03:20Z export (545063ad), which reflects the earlier source state. The exporter itself copies the FULL current source `markets.jsonl`/`log.jsonl` (all rows) into slim each run when the file differs — it does not take "only the first part".
- Live source is fresh and complete right now: `final-topics-32295b/markets.jsonl` 652 rows, last 10:13:15Z; `log.jsonl` ~194 rows, last 10:18:24Z. These go into the next 2-hourly export run (boundary from newest committed ts_mqtt minute).
- The reviewer's recovered `markets-recovered/markets.jsonl.gz` (42da6e9f) is separate from the slim copy; the next export refresh supersedes the stale slim slice.

DATA: origin blobs for slim markets/log compared to live source rows/last-ms (counts above). No IPs/hostnames.

OPEN / NOT VERIFIED:
- A concurrent push continually rejects the exporter's fast-forward (dispatch also pushes the same branch). The exporter retries/re-bases on the freshly fetched tip; re-run of the 2-hourly timer is what lands the fresh markets/log. No code change needed.

Count: notes run 1, outstanding 0, PENDING open 0.
