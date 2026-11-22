# Open mentions contracts: full-ladder own-token ask depth, 22 Nov 14:53Z (Reviewer)

Source: gamma `/events?tag_slug=mention-markets&closed=false` gave 10 open events. Gamma `public-search` for "say", "mention" and "announcers" gave the same 10. For every token I read the CLOB `/book` of that token itself (no mirroring). polymarket.com itself is blocked from this container, so this list is not yet checked against the live page.

| Event | 24h vol | Total vol | Ask $ across all levels, all tokens |
|---|---|---|---|
| Salesforce earnings call | $4,046 | $4,046 | $47,745 (16 tokens) |
| Trump/Melania Thanksgiving turkey pardon (24 Nov) | $3,852 | $13,088 | $98,131 (24 tokens) |
| Deere earnings call | $964 | $964 | $22,220 |
| Dell earnings call | $901 | $901 | $37,998 |
| Trump in November | $139 | $9,535 | $50,168 |
| Trump at China APEC | $10 | $18,431 | $18,766 |
| Trump in the Philippines | $12 | $3,351 | $2,866 |
| Caedrel / 2 NFL announcer events | $0 | stale | under $5K each |

Per token, the asks summed over all levels mostly come to $1K-6K. The best level on its own is usually $5-150.

PK's "$43-131, none reaches $200" (P-MEN-1455; it/mentions_pm_earnings_table.py:46-51) is NOT total depth. It sums only the asks priced at or below (model fair - threshold), so it is depth at a price where the model sees an edge. It covers the earnings-call family only and keeps the best single token per event. That can be a valid capacity measure, but it was reported as "depth", and the other mention families were left out.

No open mentions event shows $18-20K of 24h volume on gamma. The largest totals are APEC ($18,431, nearly all old) and the Thanksgiving pardon ($13,088, $3,852 in 24h). Which contract Nick saw is not yet matched.

## Volume by family (gamma tag mention-markets, read 22 Nov 15:00Z; lifetime volume of each event)
- Events that closed in the last 7 days: 11 events, $221,837 in total. Trump speech events: 4 events, $189,994 (the Xi/Putin trilateral alone is $163,899). Earnings calls: 5 events, $28,356. Other: 2 events, $3,487.
- Events that closed in the last 30 days: 59 events, $1,475,164 in total. Trump: 26 events, $1,259,669 (85%). Earnings calls: 19 events, $110,680 (7.5%). Other (streamers, PMQs, YouTubers, announcers): 14 events, $104,815.
- Open events now: $83,126 lifetime; $22,868 traded in the last week.
- So a backtest limited to earnings calls covered about 7.5% of 30-day mentions volume.
- Caveat: gamma `volume` is lifetime volume per event, not volume by trade date. Nick's figure of about $100K in the last week falls between the open events' week ($22.9K) and the lifetime volume of events that closed this week ($222K). A trade-dated total needs data-api trades.
