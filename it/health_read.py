#!/usr/bin/env python3
"""READ-ONLY HEALTH READ (standing rule R-037, 22 Nov 2026): run within 15 minutes of starting or restarting a recorder. Prints PASS/FAIL per bar and a final HEALTH VERDICT line.
Bars: (1) snapshots captured vs expected >= 99%, (2) 0 unhandled errors, (3) prices from the traded token's OWN book, (4) disk free and pid.
kinds:
  ws       a websocket book recorder folder (pmcs2, pmsport, pmtennis): expected = every 60 s bucket of the window holds >= 1 book row (a recorder with live games must write every minute;
           this is an OPERATIONAL definition, stated, not a vendor figure); own-book check = every row's `asset` is a token listed in markets.jsonl and carries its own bids/asks;
           errors = lines in recorder.log since the window start containing 'error' that are not a 'ws error' followed by 'ws open' (reconnect) within 60 s.
  capture  the Goalserve capture (poll logs): expected polls per sport = window / 1.8 s; captured = poll rows with recv_ns and no `err` in the window; own-book N/A (feed capture: says so).
Usage: python3 -I health_read.py ws DIR [--minutes 15] [--pid-pattern pm_sport_books]   |   python3 -I health_read.py capture GOALSERVE_DIR [--minutes 15] [--sports esports,tennis,hockey_nhl]
Override for tests: --now EPOCH."""
import argparse, collections, glob, gzip, json, os, shutil, subprocess, sys, time


def rows(path):
    op = gzip.open if path.endswith(".gz") else open
    try:
        with op(path, "rt") as f:
            for l in f:
                try:
                    yield json.loads(l)
                except Exception:
                    continue
    except (EOFError, OSError):
        return


def pid_of(pat):
    try:
        out = subprocess.run(["pgrep", "-f", pat], capture_output=True, text=True).stdout.split()
        return out[0] if out else None
    except Exception:
        return None


def out(ok, msg, fails):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        fails.append(msg)


def ws(a, now, fails):
    lo = now - a.minutes * 60
    files = sorted(glob.glob(os.path.join(a.dir, "books*.jsonl*")))
    if not files:
        out(False, "no books file under %s (nothing captured)" % a.dir, fails)
        return
    toks = set()
    mp = os.path.join(a.dir, "markets.jsonl")
    for m in rows(mp) if os.path.exists(mp) else []:
        toks.update(m.get("tokens") or [])
    n, buckets, bad_asset, empty, seen = 0, set(), 0, 0, set()
    for p in files[-3:]:
        for r in rows(p):
            t = (r.get("recv_ms") or 0) / 1000.0
            if not (lo <= t <= now):
                continue
            n += 1; buckets.add(int((t - lo) // 60)); seen.add(r.get("asset"))
            if toks and r.get("asset") not in toks:
                bad_asset += 1
            if not r.get("bids") and not r.get("asks"):
                empty += 1
    want = int(a.minutes)
    cov = 100.0 * len(buckets) / want if want else 0
    out(cov >= 99.0, "snapshots: %d rows, %d/%d one-minute buckets with data = %.1f%% (bar >= 99%%); %d distinct tokens" % (n, len(buckets), want, cov, len(seen - {None})), fails)
    errs = 0
    lp = os.path.join(a.dir, "recorder.log")
    if os.path.exists(lp):
        lines = open(lp, errors="replace").read().splitlines()[-400:]
        for i, l in enumerate(lines):
            if "error" in l.lower() and "ws error" not in l.lower():
                errs += 1
            elif "ws error" in l.lower() and not any("ws open" in x for x in lines[i + 1:i + 6]):
                errs += 1
    out(errs == 0 and empty == 0, "unhandled errors: %d in recorder.log (last 400 lines, reconnects after a ws error excluded), %d empty books in window (bar 0)" % (errs, empty), fails)
    out(bad_asset == 0 and bool(toks), "own-token book: every row's `asset` is a token in markets.jsonl and carries its own bids/asks (field `asset`, emit() in it/pm_cs2_books.js and pm_sport_books.js); rows with an unknown asset: %d; tokens listed: %d (bar 0)" % (bad_asset, len(toks)), fails)
    return


def capture(a, now, fails):
    lo = now - a.minutes * 60
    polls = collections.defaultdict(int); errs = collections.Counter()
    for p in sorted(glob.glob(os.path.join(a.dir, "goalserve_20*.jsonl")))[-2:]:
        for r in rows(p):
            for s in a.sports.split(","):
                e = r.get(s)
                if not isinstance(e, dict) or not e.get("recv_ns"):
                    continue
                if lo <= e["recv_ns"] / 1e9 <= now:
                    if "err" in e:
                        errs[s] += 1
                    else:
                        polls[s] += 1
    exp = a.minutes * 60 / 1.8
    for s in a.sports.split(","):
        c = 100.0 * polls[s] / exp
        out(c >= 99.0, "%s polls: %d of about %.0f expected (1.8 s cycle) = %.1f%% (bar >= 99%%; errors counted separately)" % (s, polls[s], exp, c), fails)
    out(sum(errs.values()) == 0, "poll errors in window: %s (bar 0; 429 = shared-key limit)" % (dict(errs) or 0), fails)
    print("INFO own-token book: not applicable to the feed capture (it stores Goalserve bodies; the Polymarket side is a separate recorder with its own read)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=("ws", "capture")); ap.add_argument("dir"); ap.add_argument("--minutes", type=float, default=15)
    ap.add_argument("--pid-pattern", default=""); ap.add_argument("--sports", default="esports,tennis,hockey_nhl"); ap.add_argument("--now", type=float)
    ap.add_argument("--floor-gb", type=float, default=10); ap.add_argument("--free-gb-test", type=float, default=None)  # floor = the recorder's own floor (small writers 5); --free-gb-test is for tests only
    a = ap.parse_args()
    now = a.now or time.time(); fails = []
    print("HEALTH READ %s kind=%s dir=%s window=%g min" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), a.kind, a.dir, a.minutes))
    (ws if a.kind == "ws" else capture)(a, now, fails)
    d = shutil.disk_usage(a.dir)
    pid = pid_of(a.pid_pattern) if a.pid_pattern else None
    free = d.free if a.free_gb_test is None else a.free_gb_test * 1e9
    out(free > a.floor_gb * 1e9 and (pid is not None or not a.pid_pattern), "disk free %.2f GB (floor %g GB); pid %s" % (free / 1e9, a.floor_gb, pid or ("n/a" if not a.pid_pattern else "NONE")), fails)
    print("HEALTH VERDICT %s%s" % ("PASS" if not fails else "FAIL", "" if not fails else " (%d bar(s) failed: on FAIL stop the run, keep the files, fix, restart, new read within 15 min)" % len(fails)))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
