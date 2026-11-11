#!/usr/bin/env bash
# TASK-thesports-export-timer-2026-11-08 step 2: 2h slim export for final-topics-32295b.
# Runs from cron every 2h. Self-bootstraps: computes SINCE from the newest ts_mqtt minute already
# committed on origin/claude/project-thread-vg2ckg, exports the window since then, plumbing-commits
# the new files (detached index, never touches the dirty worktree), pushes, refreshes the status file.
# APPROVED timer fix (Nick card 09:28Z 2026-11-09, branch thesports-timer-approved-0928):
# retry once on push rejection by re-fetching + rebuilding on the fresh tip; stage under /mnt not /tmp.
# One instance via flock on /run/writer-locks/thesports-slim.lock. Writes only to /vol + the repo.
set -u
REPO=/mnt/HC_Volume_107247271/git/pkarbs
SRC=/mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b
LOCK=/run/writer-locks/thesports-slim.lock
STAGE=/mnt/HC_Volume_107257520/pkarbs/scratch/ts_slim_stage
PY=/usr/bin/python3
EXPORTER=/root/pkarbs/live/thesports/export_slim_32295_plumb.py
MANIFEST=/mnt/HC_Volume_107257520/pkarbs/scratch/ts_slim_manifest.txt
IDX=/mnt/HC_Volume_107257520/pkarbs/scratch/idx.ts

mkdir -p "$(dirname "$LOCK")"
exec 9>"$LOCK"
if ! flock -n 9; then echo "ALREADY RUNNING: thesports-slim lock held"; exit 1; fi

cd "$REPO" || exit 1

rm -rf "$STAGE" 2>/dev/null
mkdir -p "$STAGE"

build_and_push() {
  # re-fetch, rebuild on the fresh tip, push. returns 0 on success.
  git fetch origin >/dev/null 2>&1
  TIP=$(git rev-parse origin/claude/project-thread-vg2ckg)
  [ -n "$TIP" ] || { echo "no origin tip"; return 1; }
  # boundary = newest committed ts_mqtt minute (seconds)
  LAST=$(git ls-tree -r --name-only origin/claude/project-thread-vg2ckg \
          | grep 'final-topics-32295b-slim/ts_mqtt/' | grep -oE '[0-9]{10}\.jsonl\.gz' \
          | sort -n | tail -1 | cut -d. -f1)
  SINCE=${LAST:-0}
  echo "> boundary minutes-since-epoch = $SINCE ($(date -u -d @$SINCE 2>/dev/null))"
  $PY "$EXPORTER" "$SRC/ts_mqtt.jsonl" "$SRC/books.jsonl" "$SINCE" "$STAGE" \
    rn1/scores/thesports/final-topics-32295b-slim > "$MANIFEST" 2>&1
  RC=$?
  if [ $RC -ne 0 ]; then echo "exporter rc=$RC:"; tail -5 "$MANIFEST"; return $RC; fi
  NF=$(grep -cE 'rn1/scores/thesports/final-topics-32295b-slim/' "$MANIFEST")
  NEWFILES=$(sed -n '1p' "$MANIFEST")
  if [ "${NF:-0}" = "0" ] || [ -z "$NEWFILES" ]; then echo "no new files; exit"; return 2; fi
  export GIT_INDEX_FILE=$IDX
  rm -f "$GIT_INDEX_FILE" "$GIT_INDEX_FILE.lock"
  if ! git read-tree "$TIP"; then echo "read-tree failed"; unset GIT_INDEX_FILE; return 1; fi
  n=0
  while IFS=$'\t' read -r rel size ts; do
    [ -z "$rel" ] && continue
    case "$rel" in rn1/scores/thesports/final-topics-32295b-slim/*)
      fpath="$STAGE/files/${rel#rn1/scores/thesports/final-topics-32295b-slim/}"
      if [ -f "$fpath" ]; then
        # size guard (thesports-markets-overwritten-2026-11-11): a cumulative
        # .jsonl.gz that shrank >5% vs the committed one is a truncated source,
        # never push it. Look up the committed blob size on TIP.
        case "$rel" in
          */markets.jsonl.gz|*/pmws.jsonl.gz|*/log.jsonl.gz|*/ts_poll.jsonl.gz)
            oldb=$(git ls-tree "$TIP" -- "$rel" | awk '{print $3}')
            oldsz=0
            if [ -n "$oldb" ] && [ "$oldb" != "0000000000000000000000000000000000000000" ]; then
              oldsz=$(git cat-file -s "$oldb" 2>/dev/null || echo 0)
            fi
            newsz=$(stat -c%s "$fpath")
            if [ -n "$oldsz" ] && [ "${oldsz:-0}" -gt 0 ] && [ "$newsz" -lt $(( oldsz * 95 / 100 )) ]; then
              echo "SKIP $rel: shrunk ${oldsz}->${newsz} (-$( printf '%.1f' $(echo "scale=3;100*(1-$newsz/$oldsz)"|bc) )%)" >&2
              continue
            fi;;
        esac
        blob=$(git hash-object -w "$fpath")
        git update-index --add --cacheinfo 100644,$blob,"$rel" 2>/dev/null && n=$((n+1))
      fi;;
    esac
  done < "$MANIFEST"
  TREE=$(git write-tree) || { echo "write-tree fail"; unset GIT_INDEX_FILE; return 1; }
  NOW=$(date -u +%H:%M:%SZ)
  C=$(printf 'thesports 2h slim export 32295b +%d files @%s' "$n" "$NOW" | git commit-tree "$TREE" -p "$TIP")
  unset GIT_INDEX_FILE; rm -f "$IDX" "$IDX.lock"
  git push -q origin "$C:refs/heads/claude/project-thread-vg2ckg"
  PRC=$?
  echo "> committed $C push_rc=$PRC +$n files @ $NOW"
  [ $PRC -eq 0 ]
}

build_and_push
PR=$?
if [ $PR -ne 0 ] && [ $PR -ne 2 ]; then
  echo "> first attempt rc=$PR; retrying once on fresh tip"
  rm -rf "$STAGE" 2>/dev/null; mkdir -p "$STAGE"
  build_and_push
  PR=$?
fi
[ $PR -eq 2 ] && { rm -rf "$STAGE" 2>/dev/null; exit 0; }  # no new files

# refresh status file (untracked on the thread branch)
ST=/mnt/HC_Volume_107247271/git/pkarbs/agent/status/thesports-trial.md
cat > "$ST" <<EOF
# thesports-trial status
state: running (capture-b active; 2h slim timer armed 2026-11-08; approved timer-fix applied 2026-11-09)
last export (UTC): $(date -u +%H:%M:%SZ)
push_rc: $PR
EOF
rm -rf "$STAGE" 2>/dev/null
exit $PR
