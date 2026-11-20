# 00-URGENT to IT, 20 Nov 2026 03:20Z (PandaScore thread). READ-ONLY. Right after P84a, before P83. Thanks for P85: its output is the interim view.

Two faults found in P85's paste: (A) look 1 stopped with `STOP: no capture event log` (`pandascore/events.jsonl.gz` missing) and the raw folder shows only 2 hour files; (B) every ask-depth value was NO_BOOK_ROWS, so the Polymarket recorder file has no rows for the probe's tokens. One command per line, paste all under `## PS look 1 and book-row diagnostics (20 Nov)` in `agent/status/pandascore.md`. Nothing is edited, restarted or deleted.

1. (A, local) `P=/mnt/HC_Volume_107257520/pkarbs/pandascore; ls -l --time-style=full-iso $P | head -20; ls -l --time-style=full-iso $P/raw | tail -30; ls $P/raw | wc -l; tmux ls; pgrep -af ll_capture; tail -5 /tmp/pscap2.log | cut -c1-300`
2. (A, ship rule) `cat /root/ship/writers.conf 2>&1 | head -30; grep -i pandascore /root/ship/ship.log 2>/dev/null | tail -12 | cut -c1-300`
3. (A, box; prints no variables) `. /root/ship/ship.env; rsync -e "$RSYNC_RSH" --list-only "$BOX_ROOT/pkarbs/pandascore/" 2>&1 | tail -30; rsync -e "$RSYNC_RSH" --list-only "$BOX_ROOT/pkarbs/pandascore/raw/" 2>&1 | tail -40`
4. (B, format) `B=/mnt/HC_Volume_107257520/pkarbs/pmcs2/books.jsonl; head -c 700 $B; echo; tail -c 700 $B; echo; head -3 /mnt/HC_Volume_107257520/pkarbs/pmcs2/markets.jsonl | cut -c1-500`
5. (B, are the probe's tokens in the book file; first 10 characters of each token, one grep scan per token, a few seconds each) `B=/mnt/HC_Volume_107257520/pkarbs/pmcs2/books.jsonl; for t in $(python3 -I -c "import json,glob;print(' '.join(sorted({r['token'] for f in glob.glob('/mnt/HC_Volume_107257520/pkarbs/scratch/pandascore-cs2-probe/pandascore-cs2-probe-*.json') for r in json.load(open(f))['rows']})))"); do echo "$t $(grep -c -F -- "$t" $B)"; done`

Read the result as: step 5 count 0 means the recorder never saw those tokens (market discovery gap); a count above 0 means my script's lookup is wrong (I will fix it with a test). Step 1-3 tell whether the capture and its event log exist and where the 19 Nov hour files went.
