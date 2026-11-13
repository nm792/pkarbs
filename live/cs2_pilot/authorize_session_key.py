"""NICK'S OWN COMPUTER ONLY: authorize the server's session signer to trade (CLOB only) for your deposit wallet.

Your owner key and Builder API secret are typed at hidden prompts, used in memory for this one call, and never saved,
printed or sent anywhere except Polymarket's own API. A session key can place/cancel orders but cannot withdraw.
Needs Python >= 3.11 (macOS built-in 3.9 is too old: install 3.13 from python.org, use python3.13).
Setup:  python3.13 -m pip install "polymarket-client==0.16.0"
Run:    python3 authorize_session_key.py 0xSESSION_ADDRESS 0xDEPOSIT_WALLET
Revoke: python3 authorize_session_key.py --revoke 0xSESSION_ADDRESS 0xDEPOSIT_WALLET
List:   python3 authorize_session_key.py --list - 0xDEPOSIT_WALLET
"""
import asyncio, getpass, sys
from polymarket import AsyncSecureClient, BuilderApiKey, SessionKeyKnownScope

async def main():
    args = sys.argv[1:]; mode = 'authorize'
    if args and args[0] in ('--revoke', '--list'): mode = args.pop(0)[2:]
    if len(args) != 2: sys.exit(__doc__)
    session_addr, wallet = args
    owner = getpass.getpass('Owner private key (hidden): ').strip()
    bk = BuilderApiKey(key=getpass.getpass('Builder API key (hidden): ').strip(),
                       secret=getpass.getpass('Builder API secret (hidden): ').strip(),
                       passphrase=getpass.getpass('Builder API passphrase (hidden): ').strip())
    c = await AsyncSecureClient.create(private_key=owner, wallet=wallet, api_key=bk)
    del owner
    try:
        if mode == 'authorize':
            r = await c.authorize_session_key(address=session_addr, scopes=(SessionKeyKnownScope.CLOB,))
            print('authorized (CLOB only):', r)
        elif mode == 'revoke':
            await c.revoke_session_key(address=session_addr); print('revoked', session_addr)
        for k in await c.fetch_session_keys(): print('session key on this wallet:', k)
    finally:
        await c.close()

asyncio.run(main())
