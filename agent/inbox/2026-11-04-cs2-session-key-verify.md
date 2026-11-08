# CS2 pilot: verify the session key works (read-only, no orders) — Hermes

Nick authorized session signer 0xE383138A922F2A3DE0447B13c08b2dA4Cd1ed7Fd (CLOB scope) for deposit wallet
0x8A5D1798f2A82DBB6Bd8B961f91f303EbBe5eaC7 at ~12:17Z 4 Nov. Please confirm the server can use it, WITHOUT placing orders:

In the pilot venv, as root, run this and paste ONLY its printed output into agent/outbox/cs2-session-key-verify.md:

    python3 - <<'PY'
    import asyncio
    from polymarket import AsyncSecureClient
    env = dict(l.strip().split('=',1) for l in open('/etc/pkarbs/pm-session.env') if '=' in l)
    async def main():
        c = await AsyncSecureClient.create(private_key=env['POLYMARKET_SESSION_PRIVATE_KEY'], wallet=env['POLYMARKET_DEPOSIT_WALLET'])
        try:
            ap = await c.get_trading_approvals_state()
            print('signer', c.signer.address if hasattr(c,'signer') else '?')
            print('approvals fully set:', ap.is_fully_approved, 'missing:', ap.missing)
        finally:
            await c.close()
    asyncio.run(main())
    PY

Never print the key. No orders, no LIVE_OK, no live mode. If it errors, paste the error text (it contains no key).
