#!/usr/bin/env python3
"""Compact finished Goalserve capture hour files to the winner markets only (Goalserve thread, 19 Nov 2026). Self-contained, standard library only.
Why: the full tennis/hockey capture is ~84/39 MB per hour; the signed v2 look reads only the winner market ('To Win' for tennis, 'Home/Away' for hockey/esports,
'Home/Away (map N)' for esports). Every payload is kept (same recv_ns, same JSON, same events, same team_info/info); only the non-winner entries inside each event's "odds" are dropped.
Output: the SAME file name in the SAME folder, same {"recv_ns","body"} rows (so signed v2 and the daily look need no change); a marker file <name>.compacted is left beside it.
Without --apply nothing is changed (measures and verifies only). With --apply the hour file is replaced (atomic rename) ONLY when it is older than --min-age-hours (default 3) and only after an independent re-read of both files proves
(a) same row count and recv_ns per row, (b) every event keeps all fields except odds, (c) every kept market equals the source market, (d) no winner market of the source is missing.
Usage: python3 -I compact_goalserve_hours.py --root /mnt/HC_Volume_107257520/pkarbs/goalserve --sports tennis,hockey_nhl [--min-age-hours 3] [--apply]
Never reads credentials, makes no network calls."""
import os, sys, re, json, gzip, time, argparse, glob, calendar, itertools

MAP_RE = re.compile(r"^home away (?:map|game) (\d+)$")
def norm(s): return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()
def keep_name(sport, name):
    """Same rule as the signed v2 kind_of(): tennis 'To Win'; others 'Home/Away' and 'Home/Away (map|game N)'."""
    n = norm(name)
    if sport == "tennis": return n == "to win"
    return n == "home away" or bool(MAP_RE.match(n))

def reduce_body(sport, body):
    """-> (new body string, markets_dropped). Non-JSON or unexpected shapes are returned unchanged."""
    try: d = json.loads(body)
    except Exception: return body, 0
    if not isinstance(d, dict) or not isinstance(d.get("events"), dict): return body, 0
    dropped = 0
    for eid, e in d["events"].items():
        if not isinstance(e, dict) or not isinstance(e.get("odds"), dict): continue
        keep = {}
        for mid, m in e["odds"].items():
            if isinstance(m, dict) and keep_name(sport, m.get("name")): keep[mid] = m
            else: dropped += 1
        e["odds"] = keep
    return json.dumps(d, separators=(",", ":")), dropped

def rows_of(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for l in f:
            if l.strip(): yield json.loads(l)

def hour_of(name):
    m = re.search(r"_(\d{10})\.jsonl\.gz$", name)
    return calendar.timegm(time.strptime(m.group(1), "%Y%m%d%H")) if m else None   # UTC epoch of the hour start

def compact_file(sport, src, dst):
    tmp = dst + ".tmp"
    n = dropped = 0
    with gzip.open(tmp, "wt", encoding="utf-8", compresslevel=6) as out:
        for r in rows_of(src):
            body = r.get("body")
            nb, k = reduce_body(sport, body) if isinstance(body, str) else (body, 0)
            dropped += k; n += 1
            out.write(json.dumps({"recv_ns": r.get("recv_ns"), "body": nb}, separators=(",", ":")) + "\n")
    os.replace(tmp, dst)
    return n, dropped

def verify(sport, src, dst):
    """Independent re-read of both files. -> (ok, reason)."""
    a, b = rows_of(src), rows_of(dst)
    n = 0
    for ra, rb in itertools.zip_longest(a, b):
        n += 1
        if ra is None or rb is None: return False, "row counts differ"
        if ra.get("recv_ns") != rb.get("recv_ns"): return False, "recv_ns differs at row %d" % n
        ba, bb = ra.get("body"), rb.get("body")
        if not isinstance(ba, str):
            if ba != bb: return False, "non-string body differs at row %d" % n
            continue
        try: da = json.loads(ba)
        except Exception:
            if ba != bb: return False, "bad-json body changed at row %d" % n
            continue
        db = json.loads(bb)
        if not isinstance(da, dict) or not isinstance(da.get("events"), dict):
            if da != db: return False, "payload without events changed at row %d" % n
            continue
        if {k: v for k, v in da.items() if k != "events"} != {k: v for k, v in db.items() if k != "events"}: return False, "top-level field differs at row %d" % n
        if set(da["events"]) != set(db.get("events") or {}): return False, "event set differs at row %d" % n
        for eid, ea in da["events"].items():
            eb = db["events"][eid]
            if not isinstance(ea, dict):
                if ea != eb: return False, "event %s changed at row %d" % (eid, n)
                continue
            if {k: v for k, v in ea.items() if k != "odds"} != {k: v for k, v in eb.items() if k != "odds"}: return False, "event field differs (%s) at row %d" % (eid, n)
            oa, ob = ea.get("odds"), eb.get("odds")
            if not isinstance(oa, dict):
                if oa != ob: return False, "odds changed at row %d" % n
                continue
            want = {mid: m for mid, m in oa.items() if isinstance(m, dict) and keep_name(sport, m.get("name"))}
            if ob != want: return False, "winner markets differ (event %s) at row %d" % (eid, n)
    return True, "ok rows=%d" % n

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True); ap.add_argument("--sports", required=True)
    ap.add_argument("--min-age-hours", type=float, default=3.0)
    ap.add_argument("--apply", action="store_true", help="replace the source file by the verified compact file (atomic rename); without it only measures and leaves every file as it is")
    ap.add_argument("--now", type=float, default=None, help="tests only")
    a = ap.parse_args(argv)
    now = a.now if a.now is not None else time.time()
    tot = dict(files=0, skipped_young=0, skipped_already_compact=0, verify_failed=0, replaced=0, bytes_before=0, bytes_after=0)
    for sport in a.sports.split(","):
        sd = os.path.join(a.root, "esports_payloads" if sport == "esports" else sport + "_payloads")
        for src in sorted(glob.glob(os.path.join(sd, sport + "_??????????.jsonl.gz"))):
            h = hour_of(os.path.basename(src))
            if h is None or now - (h + 3600) < a.min_age_hours * 3600: tot["skipped_young"] += 1; continue
            if os.path.exists(src + ".compacted"): tot["skipped_already_compact"] += 1; continue
            tmp = src + ".compact.tmp"
            try: compact_file(sport, src, tmp)
            except Exception as ex:
                print("FAIL compact %s: %r" % (src, ex)); tot["verify_failed"] += 1
                if os.path.exists(tmp): os.remove(tmp)
                continue
            ok, why = verify(sport, src, tmp)
            sb, sa = os.path.getsize(src), os.path.getsize(tmp)
            print("%s %s %s %d -> %d bytes" % ("OK" if ok else "VERIFY FAIL", os.path.basename(src), why, sb, sa))
            if not ok: tot["verify_failed"] += 1; os.remove(tmp); continue
            tot["files"] += 1; tot["bytes_before"] += sb; tot["bytes_after"] += sa
            if a.apply:
                os.replace(tmp, src); open(src + ".compacted", "w").close(); tot["replaced"] += 1
            else: os.remove(tmp)
    print("SUMMARY", json.dumps(tot))
    return 1 if tot["verify_failed"] else 0

if __name__ == "__main__": sys.exit(main())
