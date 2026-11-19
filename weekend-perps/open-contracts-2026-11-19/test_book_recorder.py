import datetime, json
from book_recorder import *
# slug builder
assert slugs_for(datetime.date(2026, 11, 18)) == ["spx-opens-up-or-down-on-november-18-2026", "spy-opens-up-or-down-on-november-18-2026"]
# active window: Thu 19 Nov 2026 02:00Z (Wed 21:00 ET): events for Thu 19 and Fri 20 must be active, Wed 18 (open passed) must not; Sat/Sun never
now = datetime.datetime(2026, 11, 19, 2, 0, tzinfo=datetime.timezone.utc).timestamp(); ad = active_dates(now)
assert datetime.date(2026, 11, 19) in ad and datetime.date(2026, 11, 20) in ad and datetime.date(2026, 11, 18) not in ad and all(d.weekday() < 5 for d in ad), ad
# 5 minutes after the open the event is still active, 6 minutes after it is not
o = open_ts(datetime.date(2026, 11, 19)); assert datetime.date(2026, 11, 19) in active_dates(o + 290) and datetime.date(2026, 11, 19) not in active_dates(o + 310)
# parsing: good book and error book (a 404 must be logged as err, never as an empty book)
good = book_lines(1.0, "s", "Up", "T", fetch=lambda u: {"bids": [{"price": "0.4", "size": "10"}], "asks": [{"price": "0.6", "size": "5"}]}); assert good["asks"] == [["0.6", "5"]] and "err" not in good
def boom(u): raise RuntimeError("404 No orderbook")
bad = book_lines(1.0, "s", "Up", "T", fetch=boom); assert "err" in bad and "asks" not in bad
print("RECORDER TESTS PASS")
