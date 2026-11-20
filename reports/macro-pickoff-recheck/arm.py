"""Forward macro-release book recorder + scorer (read-only, places no orders).
usage: arm.py RELEASES_JSON OUTROOT [--only NAME] [--pre 120] [--post 60]
For each release still in the future: start capture.py at R-pre-30 s, then at R+10 min run score_capture.py (provisional winners
from the last book) and again at R+26 h (resolved winners), appending one line per run to OUTROOT/results.tsv.
Run on the SERVER under cron/systemd, not in a frozen sandbox. Verify with a live read (process alive + books.jsonl.gz growing)
at least 30 min before each R (Nick 19 Nov 09:51Z). A capture with no number by the next day is a failure to raise (Nick 20 Nov)."""
import json, os, subprocess, sys, time, datetime as dt
here = os.path.dirname(os.path.abspath(__file__))
rel = json.load(open(sys.argv[1])); root = sys.argv[2]
only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
pre = int(sys.argv[sys.argv.index('--pre') + 1]) if '--pre' in sys.argv else 120
post = int(sys.argv[sys.argv.index('--post') + 1]) if '--post' in sys.argv else 60
def ts(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def score(out, rate, tag):
    p = subprocess.run([sys.executable, os.path.join(here, 'score_capture.py'), out, str(rate)], capture_output=True, text=True, timeout=600)
    open(os.path.join(out, 'score_%s.txt' % tag), 'w').write(p.stdout + p.stderr)
    try: s = json.load(open(os.path.join(out, 'summary.json')))
    except Exception: s = {'error': (p.stdout + p.stderr)[-300:]}
    with open(os.path.join(root, 'results.tsv'), 'a') as f: f.write('\t'.join([dt.datetime.utcnow().strftime('%FT%TZ'), os.path.basename(out), tag, json.dumps(s)]) + '\n')
for r in rel:
    if only and r['name'] != only: continue
    R = int(ts(r['R']))
    if R < time.time() + 60: continue
    out = os.path.join(root, r['name']); os.makedirs(out, exist_ok=True)
    while time.time() < R - pre - 30: time.sleep(5)
    subprocess.run(['timeout', str(pre + post + 120), sys.executable, os.path.join(here, 'capture.py'), out, str(R), str(pre), str(post)] + r['events'], check=False)
    while time.time() < R + 600: time.sleep(5)
    score(out, 0.05, 'provisional')
    while time.time() < R + 26 * 3600: time.sleep(60)
    score(out, 0.05, 'resolved')
