import re
# (family, regex on title, scheduled-release class). EXCLUDED: sports, weather, crypto.
FAM=[
 ("fed_decision",r"^fed (decision|interest rates)|fed decisions|fed rate (cut|hike)|how many fed rate cuts|fed emergency|fed.*dissent|dissent at the next fed","calendar"),
 ("ecb_boj_boe_bor",r"^(ecb|bank of japan|bank of england|bank of russia|bank of canada|rba|snb)\b.*(decision|interest rates)","calendar"),
 ("cpi_inflation",r"inflation (us )?- (annual|monthly)|\bcpi\b|core pce|\bpce\b","calendar"),
 ("jobs_unemp",r"jobs added|unemployment rate|nonfarm|jobless claims","calendar"),
 ("gdp",r"\bgdp\b","calendar"),
 ("eggs_prices",r"price of dozen eggs|gas price|price of eggs","calendar"),
 ("tsa_passengers",r"tsa passengers","daily-data"),
 ("earnings_beat",r"quarterly earnings|earnings (beat|per share|eps)|\beps\b","earnings"),
 ("box_office_opening",r"opening weekend|box office|domestic gross|grossing","weekly"),
 ("netflix_top",r"netflix","weekly"),
 ("spotify_chart",r"spotify","daily/weekly"),
 ("app_store_rank",r"app store|free app","daily"),
 ("elon_tweets",r"# of tweets|of tweets|\btweets\b|\bposts\b","period-end"),
 ("youtube_views",r"views of|youtube","continuous"),
 ("hormuz_ships",r"ships transit|strait of hormuz.*(ships|traffic)","weekly-data"),
 ("treasury_yield_gold",r"treasury yield|price will gold close|gold close","daily-close"),
]
SKIP=re.compile(r"\b(nba|nfl|nhl|mlb|ufc|bitcoin|btc|ethereum|eth|solana|xrp|temperature|weather|hurricane|rain|snow)\b",re.I)
EXTRA=[
 ("mentions_will_say",r"will .* (say|mention)|what will .* say|say .* during"),
 ("awards_shows",r"oscar|grammy|emmy|eurovision|golden globe|award|winner of"),
 ("resolution_by_tweet",r"tweet|post on x|truth social"),
 ("court_legal",r"court|ruling|verdict|indict|convict|trial|sentenc"),
 ("announcements_appointments",r"announce|nominate|confirm|appoint|out as|resign|fire |veto|tariff|executive order"),
 ("launches_company",r"releas|launch|gpt|model|iphone|ipo|acquir|merger|ceo"),
 ("elections_results",r"elect|win the|primary|mayor|president|senate|house|governor"),
]
SKIP2=re.compile(r"\b(vs\.?|world cup|premier league|champions league|f1|tennis|golf|nba|nfl|nhl|mlb|ufc)\b",re.I)
def classify(title):
    t=(title or "").lower()
    if SKIP.search(t): return None
    for f,rx,c in FAM:
        if re.search(rx,t): return f
    if SKIP2.search(t): return None
    for f,rx in EXTRA:
        if re.search(rx,t): return f
    return None
