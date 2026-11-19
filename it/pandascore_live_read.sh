#!/usr/bin/env bash
# READ-ONLY live read: pid + file growth over 60 s for the 3 PandaScore-side jobs. Prints OK/DOWN per job. Paste whole output.
V=/mnt/HC_Volume_107257520
sz(){ stat -c %s "$1" 2>/dev/null || echo 0; }
R=$(ls -t $V/pkarbs/pandascore/raw/*.gz 2>/dev/null | head -1); B=$V/pkarbs/pmcs2/books.jsonl
a1=$(sz "$R"); b1=$(sz "$B"); sleep 60; a2=$(sz "$R"); b2=$(sz "$B")
echo "now $(date -u +%FT%TZ)  free_GB $(df -BG --output=avail $V | tail -1 | tr -dc 0-9)"
echo "capture: pid=$(pgrep -f "ll_capture" | head -1) tmux=$(tmux ls 2>/dev/null | tr "\n" ";") newest=$R grew_60s=$((a2-a1)) $([ $((a2-a1)) -gt 0 ] && echo OK || echo DOWN-or-quiet)"
echo "pmcs2:   pid=$(pgrep -f pm_cs2_books.js | head -1) books_bytes=$b2 grew_60s=$((b2-b1)) $([ $((b2-b1)) -gt 0 ] && echo OK || echo DOWN)"
L=$(ls -t $V/pkarbs/scratch/pandascore-cs2-probe/pandascore-cs2-probe-*.log 2>/dev/null | head -1)
echo "probe:   pid=$(pgrep -f live_probe_cs2.py | head -1) loop_pid=$(pgrep -f pandascore_cs2_probe_loop | head -1) log=$L"
grep -E "PREFLIGHT|NO live|exit" "$L" 2>/dev/null | tail -8; tail -3 $V/pkarbs/scratch/pandascore-cs2-probe/probe-loop.log 2>/dev/null
