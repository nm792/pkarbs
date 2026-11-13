# To Hermes and IT, 13 Nov: APPROVED. Start the PandaScore low-latency capture NOW (new-collector item filed in agent/status/pandascore.md)

**Approval:** Nick wrote "yes" at 14:44:29Z on 13 Nov, in answer to the request to approve the PandaScore new-collector (class 4) item for today. Please record it in the approvals file against the PandaScore item as "approved by Nick, 13 Nov 14:44Z", and do NOT wait for the daily batch.

**Token:** Nick sent the PandaScore API token to Hermes in his direct chat at about 14:43Z. Install it as /etc/pkarbs/pandascore.env (PANDASCORE_TOKEN=..., mode 600). Never print, log or commit it, and never log a URL that contains it.

What to do (task: agent/tasks/TASK-pandascore-trial-2026-11-12.md v2; standard: feeds/STANDARD-feed-latency-test.md v1; guide: feeds/PandaScore-low-latency-feed-llm-guide-2026-11-13.md):
1. Confirm in agent/status/pandascore.md that the token file exists (yes/no, time UTC).
2. Build the client: discovery `GET https://api.pandascore.co/low_latency_feeds` (Bearer header) every 60 s, Dota 2 and CS2 only; sockets at `wss://live.pandascore.co/matches/{id}/low_latency_feed`, one per match, at or after `endpoint.opens_at`. Read close codes, back off only on 1xxx.
3. Charter clauses 5 and 15: log raw payloads with recv_ns (compress), under /vol2 or the storage box, nothing on the root disk. VOL2 was about 94%: check free space first and stop below the floor. Measure MB for the first hour and post an MB/day estimate.
4. Start with whatever CS2 or Dota 2 match is live or opens in the next 15 minutes. CS2 round score changes are the CS2 events until PandaScore adds kills and economy next week.
5. Status in agent/status/pandascore.md as soon as the first message is logged, then every 30 minutes while anything is open.

Deadline: first capture today; capture verified by 16 Nov 12:00Z (BLAST Slam Dota 17 Nov).
