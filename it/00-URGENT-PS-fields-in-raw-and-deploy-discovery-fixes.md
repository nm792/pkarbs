# 00-URGENT: PandaScore new-fields check (read-only) + deploy discovery fixes. Nick asked 20 Nov 03:13Z.
Run in order, paste raw output to agent/status. No file is modified in steps 1-2.

1. Live state of capture (pid + 60 s growth):
   bash /root/pkarbs/it/pandascore_live_read.sh   (after: git fetch origin reviewer; git checkout origin/reviewer -- it/)
2. Which in-round fields are in the stored payloads (newest 3 raw hour files):
   V=/mnt/HC_Volume_107257520/pkarbs/pandascore/raw; for f in $(ls -t $V/pandascore_*.jsonl.gz | head -3); do echo "== $f"; python3 -I - "$f" <<'PY'
import sys,gzip,json,collections
af=collections.Counter(); keys=collections.Counter(); n=0; bomb=0; timer=0; alive=0; side=0
for l in gzip.open(sys.argv[1],"rt"):
    try:d=json.loads(l)
    except Exception: continue
    n+=1; p=d.get("payload") or {}
    for k in (d.get("available_fields") or []): af[k]+=1
    for k in p: keys[k]+=1
    cr=p.get("current_round") or {}
    if (cr.get("bomb") or {}).get("status"): bomb+=1
    if cr.get("timer") is not None: timer+=1
    if any(pl.get("alive") is not None for t in ("home_team","away_team") for pl in (cr.get(t) or {}).get("players",[])): alive+=1
    if (cr.get("home_team") or {}).get("side"): side+=1
print("messages",n,"| available_fields counts",dict(af)); print("payload keys",dict(keys))
print("with bomb.status",bomb,"timer",timer,"player alive",alive,"side",side)
PY
   done
3. Deploy probe + recorder discovery fixes (tag_slug=counter-strike-2; gamma creation-date filter misses 17 h median):
   git fetch origin reviewer; git checkout origin/reviewer -- it/
   python3 it/REPLY-2026-11-19-test_live_probe_cs2.py   # expect PASS (6 checks)
   node it/test_pm_cs2_books.js                         # expect PASS (11 checks)
   copy it/REPLY-2026-11-19-live_probe_cs2.py and it/pm_cs2_books.js over the live copies, restart the cs2probe loop and the pmcs2 recorder.
4. Verify 15 min after restart: pid + file growth for both; grep -c of the probe tokens in books.jsonl > 0.
