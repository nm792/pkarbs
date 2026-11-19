#!/bin/bash
# One-command Dota lead run: PandaScore WS vs Polymarket own books (STANDARD v1). Read-only on inputs; writes only under $OUT.
# Usage: feeds/run_dota_lead.sh PS_DIR PMDOTA_DIR OUT_DIR        (run from a clean export of the repo, one process)
# PS_DIR     = dir of pandascore_*.jsonl.gz hourly files (e.g. /mnt/HC_Volume_107257520/pkarbs/pandascore/raw)
# PMDOTA_DIR = dir written by feeds/pm_dota_books.js (markets.jsonl, books.jsonl, books.YYYYMMDDHH.jsonl.gz)
# Output: $OUT/result.json, $OUT/audit.json, $OUT/run.log (all stderr incl. PARTIAL FILE lines), $OUT/summary.txt
set -u
PS="$1"; PM="$2"; OUT="$3"; HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT/pm"; : > "$OUT/run.log"
{
echo "== planted tests"; python3 -I "$HERE/test_ps_lead_planted.py" || { echo PLANTED_FAIL; exit 1; }
python3 -I "$HERE/test_lines_corrupt_gzip.py" || { echo GZ_TEST_FAIL; exit 1; }
python3 -I "$HERE/test_dotacap_books_adapter.py" || { echo ADAPTER_TEST_FAIL; exit 1; }
echo "== adapter"; python3 -I "$HERE/dotacap_books_adapter.py" "$PM"/books.*.jsonl.gz "$PM"/books.jsonl "$OUT/pm" || exit 1
cp "$PM/markets.jsonl" "$OUT/pm/markets.jsonl"
echo "== inputs"; ls -l --time-style=full-iso "$PS" | tail -50
echo "== lead test"; python3 -I "$HERE/ps_lead_test.py" --ps "$PS" --pm "$OUT/pm" --out "$OUT/result.json" > "$OUT/lead.stdout" || echo LEAD_EXIT_$?
echo "== audit"; python3 -I "$HERE/ps_lead_audit.py" --ps "$PS" --pm "$OUT/pm" --out "$OUT/audit.json" > "$OUT/audit.stdout" || echo AUDIT_EXIT_$?
} >> "$OUT/run.log" 2>&1
python3 -I - "$OUT" <<'PY' | tee "$OUT/summary.txt"
import json, sys
o = sys.argv[1]
try: d = json.load(open(o + "/result.json"))
except Exception as e: print("NO RESULT:", e); sys.exit(1)
print("ps_messages", d["ps_messages"], "events", d["ps_events_total"], "matches_seen", d["ps_matches_seen"], "unmatched_to_pm", d["ps_matches_unmatched_to_pm"])
for k, c in d["cells"].items():
    if k.startswith("dota"):
        print(k, "n_events", c["n_events"], "n_with_onset", c["n_with_onset"], "n_matches", c["n_matches"], "onset%", c["pct_real_with_onset"],
              "median_real", c["median_real_lead_s"], "median_placebo", c["median_placebo_lead_s"], "diff", c["diff_s"], "ci", c["ci95_match_boot"], "after%", c["pct_price_after_feed"],
              "verdict", ("UNKNOWN (n_matches<12 or n_with_onset<30)" if c["n_matches"] < 12 or c["n_with_onset"] < 30 else c["verdict"]))
PY
grep -c "PARTIAL FILE" "$OUT/run.log" | sed 's/^/partial_file_lines /'
