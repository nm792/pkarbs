// LIVE two-token TRADE-PRINT feed probe for the Nautilus paper node (R-091 item 1). Node >= 22 (global WebSocket). Paper only, read only.
// Usage: node trade_feed_probe.js <tokenA> <tokenB> [seconds=60]   Env PM_WS_URL (default Polymarket market channel).
// Subscribes to BOTH tokens of one game on the market channel and counts last_trade_price events per token (the print feed the engine's trade_execution needs).
// PASS (exit 0) only if: the socket opened with 2 tokens subscribed, BOTH tokens were acknowledged (a book or any event for each), and at least 1 last_trade_price arrived
// for at least one token within the window (run it while the game is in play; an idle window gives exit 6 'no prints'). Exit 5 = a token never acknowledged. Exit 4 = socket failed.
const [A, B, SEC] = [process.argv[2], process.argv[3], parseInt(process.argv[4], 10) || 60];
if (!A || !B || A === B) { console.error('usage: node trade_feed_probe.js <tokenA> <tokenB> [seconds]'); process.exit(2); }
const URL_ = process.env.PM_WS_URL || 'wss://ws-subscriptions-clob.polymarket.com/ws/market';
const st = { [A]: { seen: 0, trades: 0, last: null }, [B]: { seen: 0, trades: 0, last: null } }; let opened = false;
const ws = new WebSocket(URL_);
ws.onopen = () => { opened = true; ws.send(JSON.stringify({ assets_ids: [A, B], type: 'market' })); };
ws.onmessage = (ev) => {
  let d; try { d = JSON.parse(ev.data); } catch { return; }
  for (const e of Array.isArray(d) ? d : [d]) {
    const a = e.asset_id; if (!st[a]) continue; st[a].seen++;
    if (e.event_type === 'last_trade_price') { st[a].trades++; st[a].last = { price: e.price, size: e.size, side: e.side, ts: e.timestamp }; }
  }
};
ws.onerror = () => {};
setTimeout(() => {
  try { ws.close(); } catch {}
  const out = { opened, seconds: SEC, tokens: st };
  console.log(JSON.stringify(out));
  if (!opened) process.exit(4);
  if (!st[A].seen || !st[B].seen) { console.error('FAIL: a token was never acknowledged'); process.exit(5); }
  if (!st[A].trades && !st[B].trades) { console.error('FAIL: no last_trade_price on either token in the window (idle game, or the feed carries no prints)'); process.exit(6); }
  console.log('TRADE FEED PASS'); process.exit(0);
}, SEC * 1000);
