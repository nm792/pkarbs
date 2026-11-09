# 4 Nov 05:50Z from thread "Find a fast live Dota 2 feed": please run agent/tasks/dota-live-capture.md today

Nick asked for a fast Dota 2 feed (BLAST Slam starts 17 Nov). We found free Valve realtime endpoints on www.dota2.com
that the Claude sandbox cannot reach. Please start the capture before 09:45Z (it waits until then by itself), check it at 10:00Z,
copy outputs every 30 min, and write agent/status/dota-live-capture.md. Read-only, no orders, one process, 400 MB cap.
If you can reach it, also run once now and paste the first 300 bytes into the status file:
  curl -s -A "Mozilla/5.0" https://www.dota2.com/webapi/IDOTA2League/GetLiveGames/v001 | head -c 300
