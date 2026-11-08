"""Month-by-month $/day estimate for a sports portfolio, Nov 2026 - Oct 2027.
$/day = YIELD x Polymarket volume per day (22 Oct-2 Nov measured, rank/) x season factor (ESTIMATE, from usual calendars).
YIELD = LoL per-game profit over LoL volume: $60 per game (LoL thread, ~3 games per series) / $5.0M volume per series."""
import json
VOL_DAY = {   # $M per day, 22 Oct 02Z - 2 Nov 06Z (10.2 days), measured
    'LoL': 175.38 / 10.2, 'CS2': 121.17 / 10.2, 'Dota 2': 80.91 / 10.2, 'NFL': 115.43 / 10.2, 'NHL': 20.9 / 10.2,
    'Tennis (ATP+WTA)': (90.91 + 55.51) / 10.2, 'Cricket (intl)': 5.26 / 10.2, 'Rugby': 2.9 / 365}
YIELD = 60 * 3 / 5.0e6
MON = ['Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']
SEASON = {   # ESTIMATE: volume vs late Oct 2026, from usual season calendars
    'LoL':              [0.5, 0.05, 0.3, 0.4, 0.4, 0.4, 0.3, 0.4, 0.6, 0.4, 0.4, 1.0],   # Worlds ends mid-Nov; off-season Dec; MSI Jul; Worlds Oct
    'CS2':              [1.0, 0.6, 0.5, 0.9, 1.0, 1.0, 1.0, 1.1, 0.9, 0.9, 1.0, 1.0],
    'Dota 2':           [1.0, 0.5, 0.7, 0.9, 1.0, 0.9, 1.0, 1.0, 0.9, 1.0, 1.1, 0.8],
    'NFL':              [1.0, 1.0, 0.8, 0.2, 0, 0, 0, 0, 0, 0, 0.9, 1.0],
    'NHL':              [1.0, 0.9, 1.0, 0.9, 1.0, 1.2, 1.3, 0.6, 0, 0, 0, 0.9],
    'Tennis (ATP+WTA)': [0.6, 0.1, 1.2, 0.9, 1.0, 0.9, 1.1, 1.2, 1.1, 1.0, 1.0, 1.0],
    'Cricket (intl)':   [1.0, 1.5, 1.5, 1.2, 2.0, 6.0, 5.0, 1.0, 1.0, 1.5, 1.2, 1.0],   # IPL Mar-May
    'Rugby':            [1.5, 0.8, 0.8, 2.0, 2.0, 1.0, 1.2, 1.0, 0.5, 1.0, 1.0, 5.0]}   # Six Nations Feb-Mar, RWC Oct 2027
rows = {s: [round(YIELD * VOL_DAY[s] * 1e6 * f) for f in SEASON[s]] for s in SEASON}
tot = [sum(rows[s][k] for s in rows) for k in range(12)]
core = [sum(rows[s][k] for s in ('LoL', 'CS2', 'Dota 2', 'Cricket (intl)', 'Rugby', 'NHL')) for k in range(12)]
print('yield per $ volume', YIELD)
print(f"{'sport':18}" + ''.join(f'{m:>6}' for m in MON))
for s, r in rows.items(): print(f'{s:18}' + ''.join(f'{x:>6}' for x in r))
print(f"{'TOTAL':18}" + ''.join(f'{x:>6}' for x in tot))
print(f"{'excl NFL+tennis':18}" + ''.join(f'{x:>6}' for x in core))
json.dump(dict(yield_per_usd=YIELD, vol_day_musd=VOL_DAY, season=SEASON, usd_day=rows, total=tot, excl_nfl_tennis=core), open('out_calendar.json', 'w'), indent=1)
