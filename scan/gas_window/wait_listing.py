#!/usr/bin/env python3
"""Poll Gamma until the next gas event exists, log the detect time to the ns, then record all 12 books (6 buckets, YES and NO) at 1 s via pm_gas_books.py AND every trade at 1 s via pm_gas_trades.py for --record-seconds.
usage: wait_listing.py --slug S --out DIR --wait-until ISOZ --record-seconds N
Run it on the SERVER from 14:50Z each day (the event lists at about 15:00:11Z in winter, 14:00:11Z in summer time): the 19 Nov run in the session sandbox died at 15:14:25Z, most likely because the sandbox restarted (UNVERIFIED), which a server run avoids."""
import argparse, json, time, calendar, subprocess, sys, os
import pm_gas_books as b
def main(argv=None, sleep=time.sleep, now=time.time):
    ap = argparse.ArgumentParser(); ap.add_argument("--slug"); ap.add_argument("--out"); ap.add_argument("--wait-until"); ap.add_argument("--record-seconds", type=int, default=2400)
    a = ap.parse_args(argv); os.makedirs(a.out, exist_ok=True)
    end = calendar.timegm(time.strptime(a.wait_until, "%Y-%m-%dT%H:%M:%SZ")); n = 0
    while now() < end:
        t0 = now(); n += 1
        try:
            if b.event_tokens(a.slug):
                ev = b._get(f"https://gamma-api.polymarket.com/events?slug={a.slug}")[0]
                json.dump({"detect_ns": time.time_ns(), "polls": n, "created": [m.get("createdAt") for m in ev["markets"]], "start": [m.get("startDate") for m in ev["markets"]]}, open(os.path.join(a.out, a.slug + ".listing.json"), "w"))
                print("LISTED after", n, "polls", flush=True)
                here = os.path.dirname(os.path.abspath(__file__))
                subprocess.Popen([sys.executable, os.path.join(here, "pm_gas_trades.py"), "--slug", a.slug, "--out", a.out, "--until", a.wait_until, "--interval", "1", "--max-seconds", str(a.record_seconds)])   # trades of all six markets, same clock
                return subprocess.call([sys.executable, os.path.join(here, "pm_gas_books.py"), "--slug", a.slug, "--out", a.out, "--until", a.wait_until, "--interval", "1", "--max-seconds", str(a.record_seconds)])
        except (IndexError, KeyError): pass          # not listed yet: Gamma returns an empty list
        except Exception as e: print("ERR", repr(e)[:80], flush=True)      # any other failure: keep polling, never exit
        sleep(max(0.0, 0.5 - (now() - t0)))
    print("never listed", flush=True); return 1
if __name__ == "__main__": sys.exit(main())
