#!/usr/bin/env python3
"""Timer-fired launcher for scheduled captures (rugby now, chess too). Stdlib only. One short process; it starts the capture
detached and exits. It exists because window C (8 Nov) was missed: launches were manual.

  python3 capture_launcher.py rugby --window C [--config PATH] [--dry-launch]
  python3 capture_launcher.py chess --hours 6 [--dry-launch]

Steps: (1) token/market check, logged as one JSON line to ROOT/schedule/launcher.log;
(2) refuse to launch if the check fails (log FAIL, exit 1) so a bad config is seen at kickoff-15, not after;
(3) start the capture detached (start_new_session); the capture's own flock guard stops a second copy;
(4) after 60 s, verify the process is alive and the output file exists; log OK/FAIL and write one line to
ROOT/schedule/last_launch.txt (Hermes copies it into agent/status). No capture is touched if one already runs.
"""
import argparse, json, os, subprocess, sys, time, urllib.request
from datetime import datetime, timezone
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("PKARBS_ROOT", "/root/pkarbs")
SDIR = f"{ROOT}/schedule"
UA = {"User-Agent": "pkarbs-research/1.0"}
BOOK = "https://clob.polymarket.com/book?token_id="

def log(rec):
    rec["t"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(SDIR, exist_ok=True)
    with open(f"{SDIR}/launcher.log", "a") as f: f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec), flush=True)

def book_ok(tok):
    try:
        with urllib.request.urlopen(urllib.request.Request(BOOK + tok, headers=UA), timeout=15) as r:
            return r.status == 200
    except Exception:
        return False

def rugby_check(cfg_path, window):
    cfg = json.load(open(cfg_path))
    events = cfg.get(window, [])
    flat = [m for ev in events for m in ev.get("markets", [])]      # tokens live on each event's markets
    toks = [t for m in flat for t in m.get("clobTokenIds", [])]
    bad = [t[:10] for t in toks if not book_ok(t)]
    return {"kind": "rugby", "window": window, "events": len(events), "markets": len(flat), "tokens": len(toks), "book_rest_fail": bad}, (len(toks) > 0 and not bad)

def chess_check():
    out = subprocess.run([sys.executable, f"{HERE}/chess-wcc-capture.py", "--check"], capture_output=True, text=True, timeout=120).stdout
    n = 0
    for l in out.splitlines():
        if l.startswith("per-game chess markets open:"): n = int(l.split(":")[1])
    return {"kind": "chess", "open_markets": n}, n > 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["rugby", "chess"])
    ap.add_argument("--window"); ap.add_argument("--hours", default="6")
    ap.add_argument("--config", default=f"{ROOT}/agent/tasks/rugby-top14-config-2026-11-07.json")
    ap.add_argument("--dry-launch", action="store_true")
    a = ap.parse_args()
    if a.kind == "rugby":
        info, ok = rugby_check(a.config, a.window)
        cmd = [sys.executable, "-u", f"{HERE}/rugby-top14-capture.py", a.window]
        outfile = f"{ROOT}/rugby/{a.window}_clob.jsonl"; logf = f"{ROOT}/rugby/{a.window}_launch.out"
    else:
        info, ok = chess_check()
        cmd = [sys.executable, "-u", f"{HERE}/chess-wcc-capture.py", "--run", "--hours", a.hours]
        outfile = None; logf = f"{ROOT}/chess/launch.out"
    info["check"] = "PASS" if ok else "FAIL"
    log({"step": "check", **info})
    if not ok:
        open(f"{SDIR}/last_launch.txt", "w").write(f"FAIL check {json.dumps(info)}\n"); sys.exit(1)
    if a.dry_launch:
        log({"step": "dry-launch", "cmd": cmd}); return
    os.makedirs(os.path.dirname(logf), exist_ok=True)
    p = subprocess.Popen(["nice", "-n", "19"] + cmd, stdout=open(logf, "a"), stderr=subprocess.STDOUT, start_new_session=True, cwd=ROOT)
    time.sleep(60)
    alive = p.poll() is None
    exists = (os.path.exists(outfile) if outfile else True)
    res = "OK" if alive else f"EXITED rc={p.poll()} (a held flock means a copy already runs)"
    log({"step": "post-check", "pid": p.pid, "alive": alive, "outfile_exists": exists, "result": res})
    open(f"{SDIR}/last_launch.txt", "w").write(f"{res} pid={p.pid} {a.kind} {a.window or ''} tokens={info.get('tokens', '-')} outfile={exists}\n")
    sys.exit(0 if alive else 1)

if __name__ == "__main__":
    main()
