"""Log Polymarket sports WS NBA frames with receive time (answers 'ping' with 'pong'). Usage: python3 pmws.py OUT.jsonl SECONDS"""
import sys, json, time, asyncio, websockets
OUT, DUR = sys.argv[1], float(sys.argv[2]); T1 = time.time() + DUR
async def main():
    f = open(OUT, 'a')
    while time.time() < T1:
        try:
            async with websockets.connect('wss://sports-api.polymarket.com/ws', additional_headers={'User-Agent': 'Mozilla/5.0 pkarbs'}, ping_interval=None) as ws:
                while time.time() < T1:
                    m = await asyncio.wait_for(ws.recv(), timeout=60)
                    if m == 'ping': await ws.send('pong'); continue
                    if '"nba"' in m: f.write(json.dumps(dict(recv_ms=int(time.time() * 1000), data=m)) + '\n'); f.flush()
        except Exception as e:
            f.write(json.dumps(dict(recv_ms=int(time.time() * 1000), err=str(e)[:200])) + '\n'); f.flush(); await asyncio.sleep(2)
asyncio.run(main())
