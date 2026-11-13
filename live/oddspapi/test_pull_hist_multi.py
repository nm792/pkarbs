import sys, os, json, gzip, tempfile
sys.path.insert(0, '' + os.path.dirname(os.path.abspath(__file__)) + ''); import pull_hist, pull_hist_multi as M
pull_hist.COOLDOWN = {k: 0 for k in pull_hist.COOLDOWN}; os.environ['ODDSPAPI_KEY'] = 'SECRET123'
def fetch(ep, p):
    if ep == 'account': return 200, {'apiKey': 'SECRET123', 'requestsRemaining': 900}
    if ep == 'bookmakers': return 200, [{'slug': 'pinnacle'}]
    if ep == 'fixtures':
        return 200, [{'fixtureId': f"f{p['sportId']}{p['from'][5:10]}{i}", 'statusId': 2, 'startTime': p['from'], 'participant1Name': 'A', 'participant2Name': 'B',
                      'tournamentSlug': 'nba' if i == 0 else 'euroleague', 'categorySlug': 'x'} for i in range(2)]
    if ep == 'historical-odds': return 200, {'bookmakers': {}}
d = tempfile.mkdtemp(); r = M.main([d, '--cap', '3'], fetch=fetch)
log = open(f'{d}/log.jsonl').read(); files = os.listdir(f'{d}/hist')
nba = [f for f in files if f.startswith('nba_')]; lol = [f for f in files if f.startswith('lol_')]
checks = [r == 0, 'SECRET123' not in log, len(nba) == 3 and all('f11' in f for f in nba), len(lol) == 3, not any(f.startswith('nfl_f14') and 'euro' in f for f in files)]
print(checks, f"{sum(checks)} of {len(checks)} checks pass")
