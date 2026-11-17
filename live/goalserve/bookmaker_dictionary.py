#!/usr/bin/env python3
"""Goalserve pregame odds bookmaker inventory per sport (read-only, one GET per sport, no capture touched).
Question answered: which bookmakers does each Goalserve odds feed carry, and is Pinnacle one of them?
Source of truth is the odds feed itself (every <bookmaker name=".." id=".."> node under getodds/soccer?cat=<sport>_10),
plus the documented dictionary call tennis_scores/pregame_bookmakers (tried once, result recorded as-is).
Key: read from the env file (GOALSERVE_KEY). The key is NEVER printed, logged or written; URLs in errors are scrubbed.
Usage (on the server, as the capture user):
  python3 -I live/goalserve/bookmaker_dictionary.py --out agent/status/goalserve-bookmaker-dictionary-2026-11-17.md
Test (no network): python3 -I live/goalserve/test_bookmaker_dictionary.py
Done check: the output file ends with one line per sport:  'PINNACLE <sport>: yes (id N) | no | NOT CHECKED (<reason>)'.
"""
import argparse, collections, datetime, gzip, os, re, sys, urllib.request, urllib.parse

ENV_FILE = "/etc/pkarbs/goalserve.env"
BASE = "https://www.goalserve.com/getfeed"
# exact categories from the vendor email (full_package_feed.txt, PREGAME ODDS section); key = label used below
CATS = ["soccer", "basket", "tennis", "hockey", "handball", "volleyball", "football", "baseball",
        "cricket", "rugby", "rugbyleague", "boxing", "esports", "futsal", "mma", "darts"]
BM_RE = re.compile(r'<bookmaker\b([^>]*)>', re.I)
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')


def read_key(path=ENV_FILE):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("GOALSERVE_KEY="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("GOALSERVE_KEY not found in env file")


def scrub(s, key):
    return s.replace(key, "[KEY]") if key else s


def get(url, key, timeout=120):
    req = urllib.request.Request(url, headers={"Accept-Encoding": "gzip"})
    try:
        body = urllib.request.urlopen(req, timeout=timeout).read()
    except Exception as ex:  # never leak the key through an exception string
        return None, scrub(repr(ex), key)[:200]
    try:
        body = gzip.decompress(body)
    except Exception:
        pass
    return body.decode("utf-8", "replace"), None


def parse_bookmakers(text):
    """-> Counter {(name, id): occurrences}"""
    c = collections.Counter()
    for m in BM_RE.finditer(text):
        a = dict(ATTR_RE.findall(m.group(1)))
        if a.get("name"):
            c[(a["name"], a.get("id", ""))] += 1
    return c


def run(base, key, cats, days):
    today = datetime.datetime.now(datetime.timezone.utc).date()
    ds = today.strftime("%d.%m.%Y")
    de = (today + datetime.timedelta(days=days)).strftime("%d.%m.%Y")
    results = {}
    for cat in cats:
        url = f"{base}/{key}/getodds/soccer?cat={cat}_10&date_start={ds}&date_end={de}"
        text, err = get(url, key)
        if err:
            results[cat] = {"error": err}
            continue
        c = parse_bookmakers(text)
        results[cat] = {"bookmakers": c, "bytes": len(text)}
    url = f"{base}/{key}/tennis_scores/pregame_bookmakers"
    text, err = get(url, key)
    dictionary = {"error": err} if err else {"bookmakers": parse_bookmakers(text) or None, "bytes": len(text), "head": text[:200]}
    return results, dictionary, (ds, de)


def render(results, dictionary, window, now):
    out = [f"# Goalserve pregame bookmakers per sport, read-only, {now:%d %B %Y %H:%MZ}",
           "", f"Window asked of each odds feed: {window[0]} to {window[1]} (UTC). Source: the odds feed's own `<bookmaker>` nodes "
           "(`getodds/soccer?cat=<sport>_10`), one GET per sport. Pregame only (refresh about 30 s); NOT the in-play odds.", ""]
    pin = []
    for cat, r in results.items():
        out.append(f"## {cat}")
        if "error" in r:
            out.append(f"- not read: {r['error']}")
            pin.append(f"PINNACLE {cat}: NOT CHECKED ({r['error'][:60]})")
            out.append("")
            continue
        c = r["bookmakers"]
        out.append(f"- bytes read: {r['bytes']}; distinct bookmakers: {len(c)}")
        for (n, i), k in sorted(c.items(), key=lambda x: (-x[1], x[0])):
            out.append(f"  - {n} (id {i}): {k} market rows")
        hit = [(n, i) for (n, i) in c if "pinnacle" in n.lower()]
        if not c:
            pin.append(f"PINNACLE {cat}: NOT CHECKED (no bookmaker nodes in the window; feed empty or window has no matches)")
        elif hit:
            pin.append(f"PINNACLE {cat}: yes (id {hit[0][1]})")
        else:
            pin.append(f"PINNACLE {cat}: no")
        out.append("")
    out.append("## Documented dictionary call tennis_scores/pregame_bookmakers")
    if "error" in dictionary:
        out.append(f"- not read: {dictionary['error']}")
    else:
        out.append(f"- bytes {dictionary['bytes']}; first 200 chars (key-free): `{dictionary['head']}`")
        if dictionary["bookmakers"]:
            out.append("- parsed bookmakers: " + ", ".join(f"{n} (id {i})" for (n, i) in sorted(dictionary["bookmakers"])))
    out.append("")
    out.extend(pin)
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--env", default=ENV_FILE)
    ap.add_argument("--base", default=BASE)
    ap.add_argument("--days", type=int, default=1)
    ap.add_argument("--cats", default=",".join(CATS))
    a = ap.parse_args()
    key = read_key(a.env)
    res, dic, win = run(a.base, key, a.cats.split(","), a.days)
    text = render(res, dic, win, datetime.datetime.now(datetime.timezone.utc))
    assert key not in text, "key leaked into output"
    open(a.out, "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
