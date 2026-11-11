# Up/down series as rebate market-making candidates (not 5-minute BTC)
Volume = adjusted $/day (PM: events ended in last 4 days, gamma x0.5; Kalshi: 24h contracts x min(p,1-p) snapshot). Share assumed 5% of volume. Rebate/day = share x vol x taker fee per $ (rate x (1-p), p=0.5) x rebate share. Spread/day = share x vol x spread/2, GROSS before adverse selection.

| # | series | volume $/day | taker fee | maker rebate | spread | book depth within 2c ($) | rebate ceiling $/day | gross spread ceiling $/day | total ceiling $/day | note |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | PM Bitcoin 15-min | $245,795 | 7.0% | 20% | 0.7c | $2,797 | $86 | $43 | $129 |  |
| 2 | Kalshi KXBTCD (Bitcoin price Above/below) | $319,465 | 7.0% | 0% | 1.1c | $850 | $0 | $84 | $84 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 3 | PM Gold 15-min | $2,189 | 7.0% | 20% | 47.0c | $15 | $1 | $26 | $26 |  |
| 4 | PM Bitcoin hourly | $26,635 | 7.0% | 20% | 1.3c | $751 | $9 | $9 | $18 |  |
| 5 | PM Ethereum 15-min | $27,583 | 7.0% | 20% | 1.2c | $2,156 | $10 | $8 | $18 |  |
| 6 | Kalshi KXBTCMINMON (BTC one touch minimum) | $32,097 | 7.0% | 0% | 1.1c | $62 | $0 | $9 | $9 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 7 | PM S&P 500 (SPX) daily | $11,276 | 4.0% | 25% | 2.0c | $896 | $3 | $6 | $8 |  |
| 8 | PM S&P 500 (SPX) daily open | $3,753 | 4.0% | 25% | 8.0c | $220 | $1 | $8 | $8 |  |
| 9 | PM Bitcoin daily | $9,831 | 7.0% | 20% | 1.5c | $11,311 | $3 | $4 | $7 |  |
| 10 | PM Ethereum hourly | $6,296 | 7.0% | 20% | 3.0c | $345 | $2 | $5 | $7 |  |
| 11 | PM Solana 15-min | $6,960 | 7.0% | 20% | 2.0c | $170 | $2 | $3 | $6 |  |
| 12 | PM Bitcoin 240-min | $5,099 | 7.0% | 20% | 2.0c | $1,079 | $2 | $3 | $4 |  |
| 13 | PM XRP 15-min | $5,033 | 7.0% | 20% | 1.5c | $311 | $2 | $2 | $4 |  |
| 14 | PM Silver 15-min | $1,486 | 7.0% | 20% | 8.0c | $10 | $1 | $3 | $3 |  |
| 15 | Kalshi KXINXU (S&P 500 above/below) | $540 | 7.0% | 0% | 23.3c | $404 | $0 | $3 | $3 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 16 | Kalshi KXBTC (Bitcoin range) | $4,176 | 7.0% | 0% | 2.6c | $30 | $0 | $3 | $3 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 17 | PM NVIDIA (NVDA) daily | $1,203 | 4.0% | 25% | 6.0c | $255 | $0 | $2 | $2 |  |
| 18 | PM Dogecoin 15-min | $2,609 | 7.0% | 20% | 1.5c | $441 | $1 | $1 | $2 |  |
| 19 | Kalshi KXETHD (Ethereum price Above/below) | $4,295 | 7.0% | 0% | 1.5c | $127 | $0 | $2 | $2 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 20 | PM BNB 15-min | $2,174 | 7.0% | 20% | 1.5c | $251 | $1 | $1 | $2 |  |
| 21 | PM Gold (XAUUSD) daily | $1,011 | 4.0% | 25% | 5.0c | $80 | $0 | $1 | $2 |  |
| 22 | PM Ethereum daily | $2,496 | 7.0% | 20% | 1.0c | $9,845 | $1 | $1 | $1 |  |
| 23 | PM SPY (SPY) daily | $2,476 | 4.0% | 25% | 1.0c | $328 | $1 | $1 | $1 |  |
| 24 | PM Hyperliquid 15-min | $1,400 | 7.0% | 20% | 1.8c | $385 | $0 | $1 | $1 |  |
| 25 | PM Tesla (TSLA) daily | $135 | 4.0% | 25% | 27.0c | $238 | $0 | $1 | $1 |  |
| 26 | PM Ethereum 240-min | $1,036 | 7.0% | 20% | 2.0c | $218 | $0 | $1 | $1 |  |
| 27 | Kalshi KXXRPD (XRP Price above/below) | $582 | 7.0% | 0% | 5.8c | $83 | $0 | $1 | $1 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 28 | Kalshi KXBTCVSGOLD (BTC vs Gold) | $505 | 7.0% | 0% | 6.5c | $5 | $0 | $1 | $1 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 29 | PM Silver (XAGUSD) daily | $563 | 4.0% | 25% | 4.0c | $516 | $0 | $1 | $1 |  |
| 30 | PM Airbnb (ABNB) daily | $31 | 4.0% | 25% | 83.0c | $1,818 | $0 | $1 | $1 |  |
| 31 | PM Solana hourly | $884 | 7.0% | 20% | 1.0c | $93 | $0 | $0 | $1 |  |
| 32 | PM Solana daily | $858 | 7.0% | 20% | 1.0c | $1,060 | $0 | $0 | $1 |  |
| 33 | PM Russell 2000 (RUT) daily | $1,999 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 34 | PM Micron (MU) daily | $382 | 4.0% | 25% | 4.0c | $380 | $0 | $0 | $0 |  |
| 35 | PM XRP hourly | $750 | 7.0% | 20% | 1.0c | $136 | $0 | $0 | $0 |  |
| 36 | PM Netflix (NFLX) daily | $411 | 4.0% | 25% | 3.0c | $328 | $0 | $0 | $0 |  |
| 37 | PM WTI Crude Oil (WTI) daily | $406 | 4.0% | 25% | 3.0c | $347 | $0 | $0 | $0 |  |
| 38 | PM Google (GOOGL) daily | $195 | 4.0% | 25% | 7.0c | $404 | $0 | $0 | $0 |  |
| 39 | PM EWY (EWY) daily | $293 | 4.0% | 25% | 4.0c | $563 | $0 | $0 | $0 |  |
| 40 | PM SPY daily open | $14 | 4.0% | 25% | 98.0c | $466 | $0 | $0 | $0 |  |
| 41 | PM XRP daily | $398 | 7.0% | 20% | 2.0c | $1,854 | $0 | $0 | $0 |  |
| 42 | PM Solana 240-min | $305 | 7.0% | 20% | 3.0c | $287 | $0 | $0 | $0 |  |
| 43 | PM Microsoft (MSFT) daily | $219 | 4.0% | 25% | 5.0c | $255 | $0 | $0 | $0 |  |
| 44 | Kalshi KXBTC15M (BTC 15 min) | $12,641 | 7.0% | 0% | 0.1c | $356 | $0 | $0 | $0 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 45 | Kalshi KXETHMINMON (ETH min one touch monthly) | $728 | 7.0% | 0% | 1.7c | $29 | $0 | $0 | $0 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 46 | PM Coinbase (COIN) daily | $190 | 4.0% | 25% | 5.0c | $407 | $0 | $0 | $0 |  |
| 47 | PM SpaceX (SPCX) daily | $100 | 4.0% | 25% | 8.0c | $356 | $0 | $0 | $0 |  |
| 48 | PM Meta (META) daily | $210 | 4.0% | 25% | 3.0c | $461 | $0 | $0 | $0 |  |
| 49 | PM Rocket Lab (RKLB) daily | $140 | 4.0% | 25% | 5.0c | $281 | $0 | $0 | $0 |  |
| 50 | PM Dogecoin 240-min | $60 | 7.0% | 20% | 8.0c | $98 | $0 | $0 | $0 |  |
| 51 | PM XRP 240-min | $299 | 7.0% | 20% | n/a | n/a | $0 | $0 | $0 |  |
| 52 | PM Palantir (PLTR) daily | $132 | 4.0% | 25% | 2.0c | $376 | $0 | $0 | $0 |  |
| 53 | PM BNB hourly | $266 | 7.0% | 20% | n/a | n/a | $0 | $0 | $0 |  |
| 54 | PM BNB 240-min | $61 | 7.0% | 20% | 4.0c | $14 | $0 | $0 | $0 |  |
| 55 | PM Amazon (AMZN) daily | $327 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 56 | PM Dogecoin hourly | $212 | 7.0% | 20% | n/a | n/a | $0 | $0 | $0 |  |
| 57 | PM Robinhood (HOOD) daily | $28 | 4.0% | 25% | 5.0c | $466 | $0 | $0 | $0 |  |
| 58 | PM Apple (AAPL) daily | $137 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 59 | PM BNB daily | $74 | 7.0% | 20% | n/a | n/a | $0 | $0 | $0 |  |
| 60 | Kalshi KXETH15M (ETH 15 min) | $465 | 7.0% | 0% | 0.2c | $195 | $0 | $0 | $0 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 61 | PM Opendoor (OPEN) daily | $78 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 62 | PM ZCash 15-min | $18 | 7.0% | 20% | 2.0c | $40 | $0 | $0 | $0 |  |
| 63 | PM Nikkei 225 (NIK) daily | $30 | 4.0% | 25% | 0.9c | $35 | $0 | $0 | $0 |  |
| 64 | PM HYPE hourly | $37 | 7.0% | 20% | n/a | n/a | $0 | $0 | $0 |  |
| 65 | PM Dogecoin daily | $21 | 7.0% | 20% | 1.0c | $122 | $0 | $0 | $0 |  |
| 66 | PM Silver hourly | $33 | 7.0% | 20% | n/a | n/a | $0 | $0 | $0 |  |
| 67 | PM Gold hourly | $33 | 7.0% | 20% | n/a | n/a | $0 | $0 | $0 |  |
| 68 | PM Dow Jones (DJIA) daily | $34 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 69 | PM Natural Gas (NG) daily | $12 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 70 | PM FTSE 100 (UKX) daily | $11 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 71 | PM Hyperliquid 240-min | $3 | 7.0% | 20% | 2.0c | $100 | $0 | $0 | $0 |  |
| 72 | PM NYA (NYA) daily | $9 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 73 | PM DAX (DAX) daily | $9 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 74 | PM HYPE daily | $5 | 7.0% | 20% | n/a | n/a | $0 | $0 | $0 |  |
| 75 | PM Hang Seng (HSI) daily | $5 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 76 | PM US Dollar / Brazilian Real (USD/BRL) daily | $1 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 77 | PM US Dollar / Turkish Lira (USD/TRY) daily | $1 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 78 | PM US Dollar / South African Rand (USD/ZAR) daily | $1 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 79 | PM US Dollar / Swedish Krona (USD/SEK) daily | $1 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 80 | PM US Dollar / Norwegian Krone (USD/NOK) daily | $1 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 81 | PM US Dollar / Mexican Peso (USD/MXN) daily | $1 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 82 | PM US Dollar / Swiss Franc (USD/CHF) daily | $1 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 83 | PM US Dollar / South Korean Won (USD/KRW) daily | $1 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 84 | PM US Dollar / Japanese Yen (USD/JPY) daily | $1 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 85 | PM British Pound / US Dollar (GBP/USD) daily | $1 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 86 | PM Euro / US Dollar (EUR/USD) daily | $1 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 87 | PM US Dollar Index (DXY) daily | $1 | 4.0% | 25% | n/a | n/a | $0 | $0 | $0 |  |
| 88 | PM ZCash 240-min | $0 | 7.0% | 20% | 96.0c | $314 | $0 | $0 | $0 |  |
