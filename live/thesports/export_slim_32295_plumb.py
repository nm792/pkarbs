#!/usr/bin/env python3
"""TheSports slim exporter for final-topics-32295b — additive, worktree-safe.
Reads the capture chunk read-only; builds ONLY the new files (ts_mqtt minutes + books_mid q15 buckets
after SINCE_SEC, plus flat copies + counts + diary) into a STAGING dir, then commits via a detached
index seeded from the origin committed tree (git plumbing). Never touches the dirty worktree.

Layout (matches committed 32295b-slim on origin):
  <STAGE>/ts_mqtt/<hour_ms>/<minute_s>.jsonl.gz
  <STAGE>/books_mid/<hour_ms>/<q15_ms>.jsonl.gz
  <STAGE>/counts.json, log.jsonl.gz, markets.jsonl.gz, pmws.jsonl.gz, ts_poll.jsonl.gz
  <STAGE>/<repo_rel>: files the commit carries, keyed by repo-relative path under rn1/scores/thesports/.

Usage:
  export_slim_32295_plumb.py SRC SRC_BOOKS SINCE_SEC STAGE <repo>/<rel/basepath>
Writes new files under STAGE keyed by the repo path, prints them. Commit+push done by caller.
"""
import sys, os, json, gzip, shutil, collections, datetime as dt

SRC, BOOKS, SINCE, STAGE, REPO_BASE = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5]
os.makedirs(STAGE, exist_ok=True)
def utc(ms): return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc)

mqtt_new = collections.defaultdict(list)           # minute_s -> rows (ms in row)
with open(SRC, errors="replace") as f:
    for l in f:
        try: d = json.loads(l)
        except Exception: continue
        s = d["ms"] // 1000
        if s >= SINCE and d["ms"] % 1000 < 950:     # ignore the still-short trailing second bucket
            mqtt_new[s].append(d)
gm = lambda ms: ms // 1000 // 3600 * 3600 * 1000    # hour (ms) floor

written = []
for s in sorted(mqtt_new):
    hour = s // 3600 * 3600
    rel = f"{REPO_BASE}/ts_mqtt/{hour*1000}/{s}.jsonl.gz"
    base = os.path.join(STAGE, *rel.split("/"))[:-1]  # invalid for abs rel
    # STAGE is an absolute FS dir; build path = STAGE + relative-under-repo prefix
base_prefix = os.path.join(STAGE, "files")
def staged(rel):
    return os.path.join(base_prefix, rel)
for s in sorted(mqtt_new):
    rel = f"ts_mqtt/{s//3600*3600*1000}/{s}.jsonl.gz"
    p = staged(rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    with gzip.open(p, "wt") as g:
        for r in mqtt_new[s]: g.write(json.dumps(r) + "\n")
    written.append(("rn1/scores/thesports/final-topics-32295b-slim/" + rel, p))

# books_mid: q15 buckets in [SINCE_hour, now), excluding ones origin already has
import subprocess, re
now_s = int(dt.datetime.now(dt.timezone.utc).timestamp())
# origin committed buckets
comm = set()
tree = subprocess.run(["git", "ls-tree", "-r", "--name-only", "origin/claude/project-thread-vg2ckg"],
                      capture_output=True, text=True).stdout
for line in tree.splitlines():
    mm = re.search(r"32295b-slim/books_mid/\d+/(\d{13})\.jsonl\.gz$", line)
    if mm: comm.add(int(mm.group(1)))
book_new = collections.defaultdict(list)
last = {}
with open(BOOKS, errors="replace") as f:
    for l in f:
        try: d = json.loads(l)
        except Exception: continue
        b = [(float(x["price"]), float(x["size"])) for x in d.get("bids", [])]
        a = [(float(x["price"]), float(x["size"])) for x in d.get("asks", [])]
        if not b or not a: continue
        bb_, ba_ = max(b)[0], min(a)[0]; mid = (bb_ + ba_) / 2
        tk = d["tk"]; s = d["ms"] // 1000
        if last.get(tk) == s: continue
        last[tk] = s
        p2 = int(mid * 0.975 * 100) / 100
        q = sum(sz for pr, sz in b if abs(pr - p2) < 1e-9)
        bucket = d["ms"] // (15*60*1000) * (15*60*1000)
        if bucket >= SINCE*1000 and bucket < now_s*1000 and bucket not in comm:
            book_new[bucket].append((d["ms"], tk, bb_, ba_, q))
for bucket in sorted(book_new):
    rel = f"books_mid/{bucket // (3600*1000) * (3600*1000)}/{bucket}.jsonl.gz"
    p = staged(rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    with gzip.open(p, "wt") as g:
        for ms, tk, bb_, ba_, q in book_new[bucket]:
            g.write(json.dumps({"ms": ms, "tk": tk, "bb": bb_, "ba": ba_, "q": q}) + "\n")
    written.append(("rn1/scores/thesports/final-topics-32295b-slim/" + rel, p))

def _write_parts(lines, prefix, limit, out):
    """Gzip one chunk of raw lines to the next free part name; halve it if over limit."""
    p = "%s.part%03d.jsonl.gz" % (prefix, len(out) + 1)
    with gzip.open(p, "wb") as g:
        for ln in lines:
            g.write(ln)
    if os.path.getsize(p) > limit and len(lines) > 1:
        os.remove(p)
        mid = len(lines) // 2
        _write_parts(lines[:mid], prefix, limit, out)
        _write_parts(lines[mid:], prefix, limit, out)
        return
    if os.path.getsize(p) > limit:
        print("WARN single line kept whole, over limit: %s (%d B)" % (p, os.path.getsize(p)), flush=True)
    out.append(p)


def split_gz_parts(raw_path, prefix, limit, gz_full):
    """Split a cumulative raw jsonl into gz parts each <= limit bytes (project ruling
    13 Nov 16:48Z). Chunk size comes from the full-file compression ratio; cuts are on
    line boundaries so no line ever straddles two parts."""
    with open(raw_path, "rb") as fh:
        lines = fh.readlines()
    total = sum(len(x) for x in lines) or 1
    target = max(1, int(total * (limit * 0.95) / max(1, gz_full)))
    out, buf, sz = [], [], 0
    for ln in lines:
        buf.append(ln)
        sz += len(ln)
        if sz >= target:
            _write_parts(buf, prefix, limit, out)
            buf, sz = [], 0
    if buf:
        _write_parts(buf, prefix, limit, out)
    return out


# flat copies (only if changed size) + counts + diary
for n in ('markets.jsonl', 'pmws.jsonl', 'ts_poll.jsonl', 'log.jsonl'):
    srcp = os.path.join(os.path.dirname(SRC), n)
    if os.path.exists(srcp):
        # only carry if it grew (2h window) — carry unconditionally if different
        p = staged(n + ".gz"); os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(srcp, 'rb') as fi, gzip.open(p, 'wb') as go: shutil.copyfileobj(fi, go)
        gzsz = os.path.getsize(p)
        if gzsz > 950_000:
            # SPLIT route (project ruling 13 Nov 16:48Z, inbox abb9c671 / OPEN row P10):
            # an over-limit cumulative file becomes parts under 950 KB plus a one-line
            # manifest, so the repo copy stays complete. Split on LINE boundaries so each
            # part is a valid gzip on its own; readers take part001, part002, ... in order.
            os.remove(p)
            parts = split_gz_parts(srcp, staged(n), 900_000, gzsz)
            base = "rn1/scores/thesports/final-topics-32295b-slim/"
            for i, pp in enumerate(parts, 1):
                written.append(("%s%s.part%03d.jsonl.gz" % (base, n, i), pp))
            man = staged(n + ".parts.txt")
            with open(man, "w") as fh:
                fh.write(" ".join(os.path.basename(x) for x in parts) + "\n")
            written.append((base + n + ".parts.txt", man))
            print("SPLIT %s.gz %.0f B -> %d parts %s" % (
                n, gzsz, len(parts),
                ", ".join("%s=%d" % (os.path.basename(x), os.path.getsize(x)) for x in parts)),
                flush=True)
            continue
        written.append(("rn1/scores/thesports/final-topics-32295b-slim/" + n + ".gz", p))
# counts
cnt = collections.defaultdict(int)
with open(SRC, errors="replace") as f:
    for l in f:
        try: d = json.loads(l)
        except Exception: continue
        cnt["%s|%d" % (d.get('topic'), int(d['ms'] // 3600000) * 3600)] += 1
p = staged("counts.json"); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
json.dump(dict(cnt), open(p, "w")); written.append(("rn1/scores/thesports/final-topics-32295b-slim/counts.json", p))

for r, p in written:
    print("%s\t%d\t%s" % (r, os.path.getsize(p), utc(now_s*1000).strftime("%H:%M")))
print("TOTAL_FILES", len(written))
print("NOW_UTC", utc(now_s*1000).strftime("%Y-%m-%dT%H:%M:%SZ"))
