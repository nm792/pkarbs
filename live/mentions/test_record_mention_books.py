"""Offline checks for record_mention_books.py (no network)."""
import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import time,record_mention_books as R
ok=0
now=time.time()
iso=lambda age:time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(now-age))
c=[R.young(iso(60),now) is not None, R.young(iso(4*3600),now) is None, R.young(iso(-600),now) is None, R.young('bad',now) is None,
   R.ts('2026-11-09 06:40:52+00')>0, R.ts('2026-11-09T15:26:44Z')>0, R.WINDOW==10800, len(R.SERIES)==10]
for i,x in enumerate(c):print('check',i+1,'ok' if x else 'FAIL');ok+=bool(x)
print(f'{ok} of {len(c)} checks pass')
