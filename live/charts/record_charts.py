#!/usr/bin/env python3
"""Record free public chart pages (raw HTML, gzip) once per run. Read-only HTTPS, no keys.
usage: record_charts.py OUTDIR
Writes OUTDIR/charts_YYYYMMDD.jsonl.gz, one line per page per run:
 {"t": iso, "name": ..., "url": ..., "status": int, "n_rows": int, "html_gz_b64": ...}
Pages: kworb Spotify US/global daily and weekly (robots allow /), OpenRouter rankings (robots allow /).
Pages are 1 request each, 3 s apart. Stdout ends with {"ev":"done",...}."""
import sys, os, json, gzip, base64, time, re, urllib.request, datetime as D
PAGES = [
 ("spotify_us_daily","https://kworb.net/spotify/country/us_daily.html"),
 ("spotify_global_daily","https://kworb.net/spotify/country/global_daily.html"),
 ("spotify_us_weekly","https://kworb.net/spotify/country/us_weekly.html"),
 ("spotify_global_weekly","https://kworb.net/spotify/country/global_weekly.html"),
 ("openrouter_rankings","https://openrouter.ai/rankings"),
]
UA = "pkarbs-recorder/1.0 (research; low volume)"
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.status, r.read()
def main(out):
    os.makedirs(out, exist_ok=True)
    now = D.datetime.now(D.timezone.utc)
    path = os.path.join(out, "charts_%s.jsonl.gz" % now.strftime("%Y%m%d"))
    ok = 0
    with gzip.open(path, "at") as f:
        for name, url in PAGES:
            try:
                st, body = fetch(url)
                n = len(re.findall(rb"<tr", body))
                rec = {"t": now.isoformat(), "name": name, "url": url, "status": st, "n_rows": n,
                       "html_gz_b64": base64.b64encode(gzip.compress(body)).decode()}
                ok += st == 200 and n >= 50
            except Exception as e:
                rec = {"t": now.isoformat(), "name": name, "url": url, "status": 0, "n_rows": 0, "err": str(e)[:200]}
            f.write(json.dumps(rec) + "\n"); f.flush()
            print(json.dumps({"ev":"page","name":name,"status":rec["status"],"n_rows":rec["n_rows"]}))
            time.sleep(3)
    print(json.dumps({"ev":"done","pages_ok":ok,"file":path}))
if __name__ == "__main__":
    main(sys.argv[1])
