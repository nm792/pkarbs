"""Taiwan Central Election Commission (CEC) source for the pickoff paper node (Sat 28 Nov 2026 local elections). Read-only HTTP GETs.
Config (in the node logdir, both prepared and checked BEFORE the election):
  cec_urls.json : {polymarket_event_slug: CEC results JSON URL for that race}
  cec_names.json: {polymarket_event_slug: {CEC candidate name (Chinese, as CEC prints it): Polymarket market title (English)}}
A race fires only when the CEC JSON marks EXACTLY ONE candidate as elected (field ELECTED_KEYS truthy, e.g. is_victor '*') and that
candidate's name is in cec_names.json for the race. Anything else (no mark, two marks, unknown name, fetch/parse error) fires nothing.
Rows are found by walking the JSON for dicts that carry a NAME_KEYS field; field names are confirmed in the Friday pre-flight sample."""
import json, os, time, gzip, urllib.request
NAME_KEYS = ('cand_name', 'candidate_name', 'name')
ELECTED_KEYS = ('is_victor', 'is_elected', 'elected', 'victor')


def rows(obj):
    if isinstance(obj, dict):
        if any(k in obj for k in NAME_KEYS):
            yield obj
        for v in obj.values():
            yield from rows(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from rows(v)


def elected_name(doc):
    """CEC JSON -> the single elected candidate's name, or None."""
    win = []
    for r in rows(doc):
        nm = next((r[k] for k in NAME_KEYS if k in r), None)
        mark = next((r[k] for k in ELECTED_KEYS if k in r), None)
        if nm and mark not in (None, '', ' ', False, 0, '0', 'N', 'n'):
            win.append(str(nm).strip())
    win = list(dict.fromkeys(win))
    return win[0] if len(win) == 1 else None


def fetch(url, timeout=5):
    req = urllib.request.Request(url, headers={'Accept-Encoding': 'gzip', 'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
    raw = urllib.request.urlopen(req, timeout=timeout).read()
    try:
        raw = gzip.decompress(raw)
    except OSError:
        pass
    return json.loads(raw.decode('utf-8-sig'))


class Source:
    POLL_S = 1.0   # HTTP source: one request per event per second (rate limits); the publisher's own update cadence is the real floor
    def __init__(self, evs, logdir, fetcher=fetch):
        self.urls = json.load(open(os.path.join(logdir, 'cec_urls.json')))
        self.names = json.load(open(os.path.join(logdir, 'cec_names.json')))
        self.titles = {s: {m['title'] for m in mk} for s, mk in evs.items()}
        self.fetch = fetcher
        bad = [(s, en) for s, mp in self.names.items() for en in mp.values() if s in self.titles and en not in self.titles[s]]
        if bad:
            raise ValueError('cec_names.json titles not in the Polymarket event: %s' % bad[:5])

    def poll(self):
        out = []
        for slug, url in self.urls.items():
            if slug not in self.titles:
                continue
            try:
                zh = elected_name(self.fetch(url))
            except Exception as e:
                continue
            if zh and zh in self.names.get(slug, {}):
                out.append((slug, self.names[slug][zh], None, dict(cec_name=zh, url=url)))
        return out
