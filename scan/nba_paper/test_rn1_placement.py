import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
import rn1_placement as R
bad = []
cases = [(0.50, 0.48, 0.52, 'inside'), (0.48, 0.48, 0.52, 'at_bid'), (0.46, 0.48, 0.52, 'below_bid_within_2c'), (0.40, 0.48, 0.52, 'below_bid_deeper'), (0.52, 0.48, 0.52, 'at_or_above_ask'), (0.5, None, 0.52, 'no_book')]
for p, b, a, want in cases:
    got = R.classify(p, b, a)
    if got != want: bad.append(f'{p},{b},{a}: {got} != {want}')
# planted rows: book of token T has bid .48/ask .52 at t=1000 s; later row (after the fill) moves the bid to .50: a fill at .50 at t=1005 must be 'inside' (uses the earlier row, no hindsight)
books = {'T': [(1000_000, 0.48, 0.52), (1010_000, 0.50, 0.52)], 'U': [(1000_000, 0.20, 0.25)]}
fills = [{'ts': 1005, 'token_id': 'T', 'price': 0.50, 'size': 100}, {'ts': 1005, 'token_id': 'T', 'price': 0.48, 'size': 100}, {'ts': 1005, 'token_id': 'U', 'price': 0.50, 'size': 10},  # token U is a different token: its book says 0.50 is at_or_above_ask (own book only)
         {'ts': 5000, 'token_id': 'T', 'price': 0.5, 'size': 10}]  # stale book (> 60 s) -> no_book
o, n = R.run(fills, books)
exp = {'inside': 1, 'at_bid': 1, 'at_or_above_ask': 1, 'no_book': 1}
if dict(o) != exp: bad.append('planted run ' + str(dict(o)))
print('FAIL: ' + '; '.join(bad) if bad else 'PASS (7 checks)'); sys.exit(1 if bad else 0)
