# Up/down series as rebate market-making candidates (not 5-minute BTC)
Volume = adjusted $/day (PM: events ended in last 4 days, gamma x0.5; Kalshi: 24h contracts x min(p,1-p) snapshot). Share assumed 5% of volume. Rebate/day = share x vol x taker fee per $ (rate x (1-p), p=0.5) x rebate share. Spread/day = share x vol x spread/2, GROSS before adverse selection.

| # | series | volume $/day | taker fee | maker rebate | spread | book depth within 2c ($) | rebate ceiling $/day | gross spread ceiling $/day | total ceiling $/day | note |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Kalshi KXBTCD (Bitcoin price Above/below) | $319,465 | 7.0% | 0% | 1.1c | $850 | $0 | $84 | $84 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 2 | PM Ethereum 5-min | $26,985 | 7.0% | 20% | 2.0c | $230 | $9 | $13 | $23 |  |
| 3 | PM Ethereum 15-min | $27,583 | 7.0% | 20% | 1.2c | $2,156 | $10 | $8 | $18 |  |
| 4 | Kalshi KXBTCMINMON (BTC one touch minimum) | $32,097 | 7.0% | 0% | 1.1c | $62 | $0 | $9 | $9 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 5 | PM Ethereum hourly | $6,296 | 7.0% | 20% | 3.0c | $345 | $2 | $5 | $7 |  |
| 6 | Kalshi KXINXU (S&P 500 above/below) | $540 | 7.0% | 0% | 23.3c | $404 | $0 | $3 | $3 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 7 | Kalshi KXBTC (Bitcoin range) | $4,176 | 7.0% | 0% | 2.6c | $30 | $0 | $3 | $3 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 8 | Kalshi KXETHD (Ethereum price Above/below) | $4,295 | 7.0% | 0% | 1.5c | $127 | $0 | $2 | $2 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 9 | PM Ethereum daily | $2,496 | 7.0% | 20% | 1.0c | $9,845 | $1 | $1 | $1 |  |
| 10 | PM Ethereum 240-min | $1,036 | 7.0% | 20% | 2.0c | $218 | $0 | $1 | $1 |  |
| 11 | Kalshi KXXRPD (XRP Price above/below) | $582 | 7.0% | 0% | 5.8c | $83 | $0 | $1 | $1 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 12 | Kalshi KXBTCVSGOLD (BTC vs Gold) | $505 | 7.0% | 0% | 6.5c | $5 | $0 | $1 | $1 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 13 | Kalshi KXBTC15M (BTC 15 min) | $12,641 | 7.0% | 0% | 0.1c | $356 | $0 | $0 | $0 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 14 | Kalshi KXETHMINMON (ETH min one touch monthly) | $728 | 7.0% | 0% | 1.7c | $29 | $0 | $0 | $0 | Kalshi: no maker rebate on this series (fee_type quadratic) |
| 15 | Kalshi KXETH15M (ETH 15 min) | $465 | 7.0% | 0% | 0.2c | $195 | $0 | $0 | $0 | Kalshi: no maker rebate on this series (fee_type quadratic) |
