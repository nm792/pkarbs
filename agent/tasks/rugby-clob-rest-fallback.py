#!/usr/bin/env python3
"""REST book fallback for note rugby-clob-zero-check (5 s poll, pre-authorized).
Loads the live-match (13:30Z) tokens from the config, polls clob.polymarket.com/book
every 5s, appends JSONL to AB_clob_rest.jsonl. Bounded, separate process, stops after 4h.
Rows labelled '5 s poll resolution' per the task.
"""
import json, time, urllib.request
UA = {"User-Agent": "pkarbs-research/1.0"}
BOOK = "https://clob.polymarket.com/book"
CONF = "/root/pkarbs/agent/tasks/rugby-top14-config-2026-11-07.json"
OUT = "/root/pkarbs/rugby/AB_clob_rest.jsonl"

cfg = json.load(open(CONF))
TOKENS = []
for e in cfg["AB"][:2]:  # the two matches that kick off 13:30Z
    for m in e["markets"]:
        TOKENS += m["clobTokenIds"]

def get(tok):
    try:
        req = urllib.request.Request(f"{BOOK}?token_id={tok}", headers=UA)
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read()
    except Exception as e:
        return 0, repr(e).encode()

t0 = time.time()
while True:
    now_ms = int(time.time()*1000)
    for tok in TOKENS:
        st, body = get(tok)
        with open(OUT, "a") as f:
            row = {"recv_ms": now_ms, "token_id": tok, "status": st, "mode": "5s-poll"}
            try:
                row["book"] = json.loads(body)
            except Exception:
                row["err"] = body.decode(errors="replace")[:200]
            f.write(json.dumps(row) + "\n")
        time.sleep(1)  # small stagger within the 5s outer cadence
    time.sleep(5)
    if time.time() - t0 > 4*3600:
        break
