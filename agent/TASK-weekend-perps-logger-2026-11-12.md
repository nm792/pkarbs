# Task for the server agent: weekend perp price logger (data only)

From: Claude in the "PK arbs" project, on Nick's instruction (12 Nov 2026). Status: OPEN
Rule: weekend-perps/LOCKED-RULE.md (read it first).

## Hard rules
- Data only. No orders, no keys, no account, no signing. Public read-only endpoint api.hyperliquid.xyz/info.
- If the endpoint is unreachable or refuses the server, STOP and write outbox/weekend-perps-blocked.md with the exact error. Do not use proxies, VPNs or any workaround.
- Follow the data-disk charter: raw files on /vol2, not the root disk. Keep raw files, do not commit.

## Steps
1. Smoke test now: `python3 weekend-perps/hl_weekend_logger.py --out /vol2/weekend-perps --interval 60` for 5 minutes. Report in outbox/weekend-perps-smoke.md: reachable yes/no, dex names found, which symbols matched (Hang Seng, Nikkei, S&P, Nasdaq, Samsung, SK Hynix, US stocks), line count, any errors. The logger was written without live API access, so fix field names if needed and say what you changed.
2. If OK, run it as a restarting service through this weekend (Fri 13 Nov to Mon 16 Nov) and continuing.
3. Also check whether the venue offers historical candles for these symbols (for a backfill) and report in the smoke note.
