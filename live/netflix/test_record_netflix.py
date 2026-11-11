import sys; sys.path.insert(0,'live/netflix')
from record_netflix import parse_wn
h=open('live/netflix/fixture_wn_2026-10-14.html').read()
p=parse_wn(h)
ok=[p['date']=='2026-10-14', len(p['country'])==12, len(p['country']['US']['tv'])==10, len(p['country']['US']['movie'])==10, p['global']['movie'][0][1]=='Animals']
print(sum(ok),'of 5 checks pass')
