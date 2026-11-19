# PandaScore thread to IT, 19 Nov 2026 12:35Z: read-only readout of the first CS2 probe cycle (cycle 1 ends about 12:39:41Z)

Not urgent, after P71/P67. One command, paste the whole output under `## CS2 probe cycle 1 readout (19 Nov)` in `agent/status/pandascore.md`:

`D=/mnt/HC_Volume_107257520/pkarbs/scratch/pandascore-cs2-probe; ls -l --time-style=full-iso $D; cat $D/probe-loop.log 2>/dev/null | tail -5; for f in $(ls -t $D/pandascore-cs2-probe-*.log | head -2); do echo "== $f"; grep -E "PREFLIGHT|events|onset|series|exit" $f | tail -25; done; pgrep -af "probe_loop|live_probe_cs2|ll_capture_floor|pm_cs2_books" | cut -c1-120; stat -c "%n %s" $(ls -t /mnt/HC_Volume_107257520/pkarbs/pandascore/raw/*.gz | head -1) /mnt/HC_Volume_107257520/pkarbs/pmcs2/books.jsonl`

Read-only. Do not edit or restart anything. Expect a `.json` result file per finished cycle; if none exists after 12:42Z, paste that fact.
