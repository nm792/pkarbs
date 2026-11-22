#!/usr/bin/env python3
"""Read-only size and content profile of the Polymarket book recorder folder (Goalserve thread, 19 Nov 2026). Standard library only, reads at most TAIL bytes of each file.
Prints: every file with size and mtime; the row keys of markets/books; markets by `sport`; and, for the last TAIL bytes of books*.jsonl*, the share of bytes and rows whose token belongs to each sport.
Usage: python3 -I pm_folder_stats.py <folder> [TAIL_MB=20]"""
import sys, os, json, time, collections, gzip

def tail_lines(p, nbytes):
    sz = os.path.getsize(p)
    with open(p, "rb") as f:
        f.seek(max(0, sz - nbytes)); data = f.read()
    if p.endswith(".gz"):
        return []                                    # gz tails cannot be cut mid-stream; report size only
    parts = data.split(b"\n")
    return parts[1:-1] if sz > nbytes else parts[:-1]

def main(folder, tail_mb=20):
    tail = int(tail_mb * 1e6)
    print("folder", folder, time.strftime("%FT%TZ", time.gmtime()))
    files = sorted((os.path.join(dp, n) for dp, _, ns in os.walk(folder) for n in ns), key=lambda p: -os.path.getsize(p))
    tot = sum(os.path.getsize(p) for p in files)
    print("files", len(files), "total_bytes", tot)
    for p in files[:25]:
        print("  %14d  %s  %s" % (os.path.getsize(p), time.strftime("%m-%d %H:%M:%S", time.gmtime(os.path.getmtime(p))), os.path.relpath(p, folder)))
    tok2sport, sports = {}, collections.Counter()
    mk = [p for p in files if os.path.basename(p).startswith("markets") and not p.endswith(".gz")]
    for p in mk[:1]:
        keys = collections.Counter()
        for l in open(p, "rb"):
            try: m = json.loads(l)
            except Exception: continue
            keys.update(m.keys()); sp = m.get("sport") or "?"; sports[sp] += 1
            for t in m.get("tokens") or []: tok2sport[str(t)] = sp
        print("markets file", os.path.basename(p), "rows", sum(sports.values()), "keys", dict(keys.most_common(20)))
        print("markets by sport", dict(sports.most_common(30)))
    for p in [f for f in files if "books" in os.path.basename(f) and not f.endswith(".gz")][:3]:
        by_b, by_r, keys = collections.Counter(), collections.Counter(), collections.Counter()
        for l in tail_lines(p, tail):
            try: r = json.loads(l)
            except Exception: by_r["bad_json"] += 1; continue
            keys.update(r.keys()); sp = tok2sport.get(str(r.get("tk") or r.get("asset")), "unmapped")
            by_b[sp] += len(l) + 1; by_r[sp] += 1
        tb = sum(by_b.values()) or 1
        print("books file", os.path.basename(p), "tail_MB", tail_mb, "row keys", dict(keys.most_common(12)))
        print("  bytes share by sport (last %s MB):" % tail_mb, {k: "%.1f%%" % (100.0 * v / tb) for k, v in by_b.most_common(12)})
        print("  rows by sport:", dict(by_r.most_common(12)))

if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 20)
