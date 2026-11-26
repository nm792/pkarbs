"""winners.json from Gamma outcomePrices for the conditions in markets.jsonl (resolution, used for scoring only). Usage: python3 -I make_winners.py DIR > winners.json
Asserts every returned conditionId is one requested; a market not closed or without a 1/0 price is OMITTED (scorer then skips it, never guesses)."""
import sys, os, json, urllib.parse, urllib.request
def winner(m):
    pr = json.loads(m.get('outcomePrices') or '[]'); oc = json.loads(m.get('outcomes') or '[]')
    if not m.get('closed') or len(pr) != len(oc) or sorted(float(x) for x in pr) != [0.0, 1.0]: return None
    return oc[[float(x) for x in pr].index(1.0)]
def fetch(conds):
    out = {}
    for i in range(0, len(conds), 20):
        b = conds[i:i + 20]
        q = urllib.parse.urlencode([('condition_ids', c) for c in b] + [('limit', len(b)), ('closed', 'true')])
        for m in json.load(urllib.request.urlopen(urllib.request.Request('https://gamma-api.polymarket.com/markets?' + q, headers={'User-Agent': 'x'}), timeout=60)):
            if m['conditionId'].lower() not in {c.lower() for c in b}: raise SystemExit('WRONG MARKET from gamma: ' + m['conditionId'])
            w = winner(m)
            if w: out[m['conditionId']] = w
    return out
if __name__ == '__main__':
    conds = [json.loads(l)['cond'] for l in open(os.path.join(sys.argv[1], 'markets.jsonl'))]
    print(json.dumps(fetch(conds)))
