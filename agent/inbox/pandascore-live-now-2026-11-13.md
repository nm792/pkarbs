# PandaScore Low Latency Feed is ACTIVE (13 Nov 2026 14:03Z): start the capture today

PandaScore activated the feed for Dota 2 and CS2 until 1 December. Task rewritten as v2: agent/tasks/TASK-pandascore-trial-2026-11-12.md. Guide: feeds/PandaScore-low-latency-feed-llm-guide-2026-11-13.md. Standard: feeds/STANDARD-feed-latency-test.md v1.

Need from Hermes today:
1. Check whether /etc/pkarbs/pandascore.env (PANDASCORE_TOKEN) exists. If not, write "token missing" in agent/status/pandascore.md; the coordinator will ask Nick once. Do not ask Nick to relay.
2. Build the client per the v2 task (correct URL is `/matches/{id}/low_latency_feed`, discovery at `/low_latency_feeds`, 3 sockets per match, read close codes, never log the token).
3. File the charter APPROVALS item for a new class-4 collector if required, with exact change and revert.
4. First status in agent/status/pandascore.md by 14:45Z, then every 30 minutes while blocked. Capture running and verified by 16 Nov 12:00Z (BLAST Slam Dota 17 Nov).

IT issue #283 (Hermes never acknowledged the first version) stays open until a status file exists.
