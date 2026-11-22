#!/bin/bash
# READ-ONLY: pid + file growth 60 s apart for every Goalserve / PandaScore / Polymarket book recorder (Reviewer R-024). Prints a table, no secrets, no writes.
# Usage: bash read_all_recorders.sh        Overrides for tests: V, GAP (seconds, default 60)
V=${V:-/mnt/HC_Volume_107257520}; P=$V/pkarbs; GAP=${GAP:-60}
newest() { find "$1" -type f ! -name '*.log' -printf '%T@ %s %p\n' 2>/dev/null | sort -n | tail -1; }      # epoch size path
sz() { local f=$(echo "$1" | cut -d' ' -f3-); [ -n "$f" ] && stat -c %s "$f" 2>/dev/null || echo 0; }
declare -A DIR PAT
DIR[goalserve_esports]=$P/goalserve/esports_payloads;  PAT[goalserve_esports]='capture.py|capture_store_all.py'
DIR[goalserve_tennis]=$P/goalserve/tennis_payloads;    PAT[goalserve_tennis]='capture.py|capture_store_all.py'
DIR[goalserve_hockey_nhl]=$P/goalserve/hockey_nhl_payloads; PAT[goalserve_hockey_nhl]='capture.py|capture_store_all.py'
DIR[pandascore_raw]=$P/pandascore/raw;                 PAT[pandascore_raw]='ll_capture'
DIR[cs2_probe]=$P/scratch/pandascore-cs2-probe;        PAT[cs2_probe]='probe'
DIR[pmcs2]=$P/pmcs2;                                   PAT[pmcs2]='pm_cs2_books'
DIR[pmdota]=$P/pmdota;                                 PAT[pmdota]='pm_dota_books'
DIR[pmsport_nhl]=$P/pmsport;                           PAT[pmsport_nhl]='pm_sport_books'
DIR[final_topics_books]=$P/thesports/final-topics-32295b; PAT[final_topics_books]='capture.py'
KEYS="goalserve_esports goalserve_tennis goalserve_hockey_nhl pandascore_raw cs2_probe pmcs2 pmdota pmsport_nhl final_topics_books"
echo "READ $(date -u +%FT%TZ) gap ${GAP}s"
declare -A A
for k in $KEYS; do A[$k]=$(newest "${DIR[$k]}"); done
sleep "$GAP"
printf '%-22s %-8s %-28s %-12s %s\n' recorder pid newest_file_mtime_age_s size_before size_after_growth
for k in $KEYS; do
  b=${A[$k]}; n=$(newest "${DIR[$k]}")
  pid=$(pgrep -f "${PAT[$k]}" 2>/dev/null | head -1)
  f=$(echo "$n" | cut -d' ' -f3-); age=$(( $(date +%s) - $(echo "$n" | cut -d. -f1 | cut -d' ' -f1 | sed 's/^$/0/') ))
  s0=$(echo "$b" | cut -d' ' -f2); s1=$(echo "$n" | cut -d' ' -f2)
  [ -z "$f" ] && { printf '%-22s %-8s NO FILE under %s\n' $k "${pid:-none}" "${DIR[$k]}"; continue; }
  g=UNCHANGED; [ "$(echo "$b" | cut -d' ' -f3-)" != "$f" ] && g="NEWFILE"; [ "${s1:-0}" -gt "${s0:-0}" ] 2>/dev/null && [ "$g" = UNCHANGED ] && g="GREW+$(( s1 - s0 ))"
  printf '%-22s %-8s %-8s %-30s %s -> %s %s\n' $k "${pid:-NONE}" "${age}s" "$(basename "$f")" "${s0:-0}" "${s1:-0}" "$g"
done
echo "VOL2 free bytes: $(df -B1 --output=avail "$V" | tail -1)"
