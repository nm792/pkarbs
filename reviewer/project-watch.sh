#!/bin/bash
# Project-side watcher for the Reviewer dialogue (reviewer/PROTOCOL.md).
# Usage (from inside the project's repo clone):  bash project-watch.sh <proj>
#   <proj> = temperature | mfw | pkarbs | webb | asx
# Fetches origin/reviewer every 150 s. Exits (waking the session) when
# reviewer/<proj>/OUTBOX.md gains a new R-row or a REVIEW-RESPONSE file lands.
# Also exits after ~115 min with WATCH RESTART so a 2 h background limit never kills it silently.
# On exit: act on the row, append "| R-nnn | <UTC> | acked | ... |" to reviewer/<proj>/INBOX.md,
# reply (INBOX row or reviewer/REPLY-*.md) on the reviewer branch, push, then restart this script.
p=${1:?usage: project-watch.sh <proj>}
f="reviewer/$p/OUTBOX.md"
timeout 60 git fetch -q origin reviewer 2>/dev/null
base=${BASE:-$(git rev-parse origin/reviewer)}
for i in $(seq 1 46); do
  sleep ${SLEEP:-150}
  timeout 60 git fetch -q origin reviewer 2>/dev/null
  new=$(git rev-parse origin/reviewer)
  [ "$new" = "$base" ] && continue
  rows=$(git diff "$base" "$new" -- "$f" | grep -E '^\+\| *R-[0-9]+' | sed 's/^+//')
  resp=$(git diff --name-only "$base" "$new" -- 'reviewer/REVIEW-RESPONSE*' "reviewer/$p/" | grep -vE 'INBOX.md|OUTBOX.md')
  base=$new
  if [ -n "$rows$resp" ]; then
    date -u +"REVIEWER WAKE %FT%TZ ($p). Act now, ACK each R-row in reviewer/$p/INBOX.md, reply, push, restart the watcher."
    [ -n "$rows" ] && printf '%s\n' "$rows"
    [ -n "$resp" ] && printf 'files: %s\n' $resp
    exit 0
  fi
done
date -u +"WATCH RESTART %FT%TZ ($p): normal 115-min exit, nothing new. Restart the watcher now."
