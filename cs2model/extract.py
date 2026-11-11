#!/usr/bin/env python3
"""Step 1: pull every TheSports CS2 (csgo topic) message from all slim chunks into one compact per-map file.
Usage: extract.py OUT.jsonl.gz   (dedupes overlapping chunks by (ms, payload hash)).
Per message keeps: t (receive s), match_id, map_id, box, round_num, timer, home/away side + c_score + per-player (alive, hp, money),
events (all typeids, unchanged)."""
import sys, json, gzip, glob, hashlib
ROOT = '/home/user/repo/rn1/scores/thesports/'
DIRS = ['final-topics-8917-slim', 'slim-1102-32295', 'slim-0517-32295', 'final-topics-32295-slim', 'final-topics-32295b-slim', 'final-topics-24925']
seen = set(); n = 0
with gzip.open(sys.argv[1], 'wt') as out:
    for d in DIRS:
        files = sorted(glob.glob(ROOT + d + '/ts_mqtt/**/*.gz', recursive=True)) + sorted(glob.glob(ROOT + d + '/ts_mqtt*.gz'))
        for f in files:
            for l in gzip.open(f, 'rt'):
                try: r = json.loads(l)
                except Exception: continue
                if not r['topic'].endswith('csgo/match/v1'): continue
                h = (r['ms'], hashlib.md5(r['p'].encode()).hexdigest())
                if h in seen: continue
                seen.add(h)
                try: ps = json.loads(r['p'])
                except Exception: continue
                for p in ps:
                    def side(x):
                        return dict(id=x.get('id'), side=x['side'], c=x['c_score'], m=x.get('m_score'), fh=x.get('fh_score'), sh=x.get('sh_score'), sc=x.get('score'),
                                    pl=[(q['name'], q['stats'][4], q['stats'][7], q['stats'][8], q['stats'][0], q['stats'][1], q.get('weapon_id',''), q['stats'][6], q['stats'][3], q['stats'][2]) if len(q['stats']) >= 9 else (q['name'],) for q in x['players']])
                    out.write(json.dumps(dict(t=r['ms'] / 1000.0, mid=p['match_id'], map=p.get('map_id'), box=p.get('box_num'), st=p.get('status_id'),
                        rn=p.get('round_num'), tm=p.get('timer'), h=side(p['home']), a=side(p['away']), ev=p['event'], src=d)) + '\n')
                    n += 1
print('messages', n)
