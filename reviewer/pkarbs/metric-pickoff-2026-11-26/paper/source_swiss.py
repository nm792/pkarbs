"""Swiss federal vote (Sun 29 Nov 2026) source: official live open-data JSON of the Federal Statistical Office
(https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-20261129-eidgAbstimmung.json; URL confirmed in the pre-flight, override with swiss_url.txt).
A proposal is decided only when the JSON says vorlageBeendet true; then vorlageAngenommen (True/False) is its outcome.
swiss_titles.json in logdir: {Polymarket market title: vorlagenId} (written by hand before the vote). Fires one MAP: release per event with
every mapped market whose proposal is finished; markets not finished or not mapped are not traded."""
import json, os, gzip, urllib.request
DEFAULT_URL = 'https://ogd-static.voteinfo-app.ch/v1/ogd/sd-t-17-02-20261129-eidgAbstimmung.json'


def fetch(url, timeout=5):
    req = urllib.request.Request(url, headers={'Accept-Encoding': 'gzip', 'User-Agent': 'pickoff-paper', 'Cache-Control': 'no-cache'})
    raw = urllib.request.urlopen(req, timeout=timeout).read()
    try:
        raw = gzip.decompress(raw)
    except OSError:
        pass
    return json.loads(raw)


def finished(doc):
    """-> {vorlagenId: accepted bool} for proposals with vorlageBeendet true."""
    out = {}
    for v in ((doc or {}).get('schweiz') or {}).get('vorlagen') or []:
        if v.get('vorlageBeendet') is True and v.get('vorlageAngenommen') in (True, False):
            out[int(v['vorlagenId'])] = bool(v['vorlageAngenommen'])
    return out


class Source:
    def __init__(self, evs, logdir, fetcher=fetch):
        p = os.path.join(logdir, 'swiss_url.txt')
        self.url = open(p).read().strip() if os.path.exists(p) else DEFAULT_URL
        self.map = {k: int(v) for k, v in json.load(open(os.path.join(logdir, 'swiss_titles.json'))).items()}
        self.evs, self.fetch, self.sent = evs, fetcher, set()

    def poll(self):
        try:
            fin = finished(self.fetch(self.url))
        except Exception:
            return []
        out = []
        for slug, mk in self.evs.items():
            o = {m['title']: fin[self.map[m['title']]] for m in mk if m.get('title') in self.map and self.map[m['title']] in fin}
            if o and len(o) == sum(1 for m in mk if m.get('title') in self.map):   # fire once, when every mapped proposal is final
                out.append((slug, 'MAP:' + json.dumps(o), None, dict(url=self.url)))
        return out
