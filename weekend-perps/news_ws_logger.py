#!/usr/bin/env python3
"""Log a push news WebSocket with a LOCAL receive time (ns). Read-only. Keys come from env vars, never from Git.
Alpaca (Benzinga-sourced): wss://stream.data.alpaca.markets/v1beta1/news
  env ALPACA_KEY, ALPACA_SECRET. Messages: [{"T":"n","id":..,"headline":..,"created_at":..,"updated_at":..,"symbols":[..],"source":..}]
UNTESTED against the live feed when written (no route from the author's container): first run is a smoke test.
Usage: python3 news_ws_logger.py --out /vol2/news/alpaca_news.jsonl.gz   (pip install websockets)
"""
import argparse, asyncio, gzip, json, os, time
import websockets

URL = "wss://stream.data.alpaca.markets/v1beta1/news"

async def run(out):
    backoff = 1
    while True:
        try:
            async with websockets.connect(URL, max_size=None, ping_interval=20) as ws:
                await ws.send(json.dumps({"action": "auth", "key": os.environ["ALPACA_KEY"], "secret": os.environ["ALPACA_SECRET"]}))
                await ws.send(json.dumps({"action": "subscribe", "news": ["*"]}))
                backoff = 1
                with gzip.open(out, "at") as f:
                    async for raw in ws:
                        t = time.time_ns()
                        f.write(json.dumps({"recv_ns": t, "raw": raw if isinstance(raw, str) else raw.decode("utf-8", "replace")}) + "\n")
                        f.flush()
        except Exception as e:
            print("ws error", repr(e), flush=True)
            await asyncio.sleep(backoff); backoff = min(backoff * 2, 60)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True)
    asyncio.run(run(ap.parse_args().out))
