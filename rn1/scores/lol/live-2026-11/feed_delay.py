"""Feed delay from capture.js output: for each new newest-frame timestamp, delay = recv_ms of the first poll
that saw it minus the frame's own timestamp. Upper bound includes up to one poll interval (2 s).
Usage: python3 feed_delay.py <label>_polls.jsonl"""
import json, sys, datetime as dt, numpy as np
seen = {}
for l in open(sys.argv[1]):
    p = json.loads(l)
    if not p.get('newest_ts'): continue
    k = (p['game'], p['newest_ts'])
    if k not in seen: seen[k] = p['recv_ms'] / 1000 - dt.datetime.fromisoformat(p['newest_ts'].replace('Z', '+00:00')).timestamp()
d = np.array(list(seen.values()))
if len(d): print(f"n {len(d)} frames; delay s: min {d.min():.1f} median {np.median(d):.1f} p90 {np.percentile(d, 90):.1f} max {d.max():.1f}")
