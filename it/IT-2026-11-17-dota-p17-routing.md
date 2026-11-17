# IT note 17 Nov 21:10Z: Dota analysis + BLAST Slam capture routed

1. Goal: measure how far Polymarket Dota 2 game-winner prices lag Valve's live game state, to judge a fast-feed edge.
2. Where it stands: the 16-17 Nov capture finished but failed the window/coverage bar (agent report pkarbs c5dc7dfd, 20:46Z); raw data never reached the repo, so no lag numbers exist yet for 16-17 Nov (unsupported until P17a lands).
3. Most important: P17a, the server-side lag.py run on the 16-17 Nov local files, because it is the only way to get any result from that capture before the files age out.

Routed from agent/inbox/2026-11-17-dota-analyse-and-blast.md (44288014):
- P17a (open now): Part A exactly as written, without `git pull` (the /root/pkarbs checkout is still dirty, P16s), committing only the two result files with a path-limited commit.
- P17b (waiting until 20 Nov 10:00Z): Part B capture start, using the committed config.json as is.
- P17c (waiting until after 21 Nov 00:30Z): lag.py on the 20-21 Nov capture and the status file.

NEEDS CHUNKING (not routed): "add later days by re-running this config build when Polymarket lists them". There is no named script or command for the config build. Send a new chunk with the exact command and output path if you want later days captured.

Note for you to check (not routed): the first config.json entry is labelled `dota2-ic-all2-2026-11-13` but scheduled 20 Nov 10:00Z, which is before the 10:30Z window start; confirm the config is the one you intend.
