"""SERVER (Hermes runs this once): create a fresh trade-only session signer for the CS2 pilot.

Writes the session private key to /etc/pkarbs/pm-session.env (dir 700, file 600, root) and prints ONLY its address.
The key never leaves the server and is never printed, logged or committed. It can trade for Nick's deposit wallet only
after Nick authorizes this address from his own computer (authorize_session_key.py); a session key cannot withdraw.
Usage: python3 gen_session_key.py DEPOSIT_WALLET_ADDRESS     (the deposit wallet address is public; Nick gives it)
"""
import os, sys
from eth_account import Account

FN = os.environ.get('PM_KEY_FILE', '/etc/pkarbs/pm-session.env')
if len(sys.argv) != 2 or not sys.argv[1].startswith('0x') or len(sys.argv[1]) != 42:
    sys.exit('usage: gen_session_key.py 0xDEPOSIT_WALLET_ADDRESS')
if os.path.exists(FN):
    sys.exit(f'{FN} already exists: not overwriting (revoke the old key first, then delete the file)')
os.makedirs(os.path.dirname(FN), mode=0o700, exist_ok=True); os.chmod(os.path.dirname(FN), 0o700)
acct = Account.create()
old = os.umask(0o077)
try:
    with open(FN, 'x') as f:
        f.write(f'POLYMARKET_SESSION_PRIVATE_KEY=0x{acct.key.hex().removeprefix("0x")}\n'
                f'POLYMARKET_DEPOSIT_WALLET={sys.argv[1]}\n')
finally:
    os.umask(old)
os.chmod(FN, 0o600)
print('session signer address (give this to Nick):', acct.address)
