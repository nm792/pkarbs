# Trading key for the CS2 pilot: session key only

**Rule (Nick, 4 Nov 2026 08:56Z): neither Claude nor Hermes nor the server may ever hold a key that can withdraw or
drain the account.** No owner/account private key ever goes on the server, to Hermes, into chat, or into Git.

Mechanism: Polymarket Session Keys (docs /trading/session-keys): "A Session Key is a separate signer that a Deposit
Wallet Owner authorizes to trade for a Deposit Wallet ... A Session Key cannot withdraw funds from the Deposit Wallet."
Nick confirmed 4 Nov that the account has Builder keys and session keys are authorised.

## Steps
1. **Nick** gives Hermes the deposit wallet address (public, like a bank account number; safe to share).
2. **Hermes** (server, root): `python3 live/cs2_pilot/gen_session_key.py 0xDEPOSIT_WALLET` using the pilot venv.
   It writes `/etc/pkarbs/pm-session.env` (dir 700, file 600) and prints only the session signer address.
   Hermes reports that address in agent/outbox/cs2-pilot.md. Never print, copy or commit the file.
3. **Nick**, on his own computer (needs Python >= 3.11; macOS built-in Python 3.9 fails with "No matching distribution", so install 3.13 from python.org and use `python3.13`): `python3.13 -m pip install "polymarket-client==0.16.0"` then
   `python3.13 authorize_session_key.py 0xSESSION_ADDRESS 0xDEPOSIT_WALLET` (file is in this folder). It asks for his
   owner key and Builder key/secret/passphrase at hidden prompts, authorizes CLOB-only trading for that address,
   and lists the wallet's session keys. Nothing is saved. Revoke any time with `--revoke`.
4. **Go live** only after the dry-run report and Nick's explicit "go live" in chat. Hermes then restarts the pilot on
   current main with `--mode live` and writes `OUT/LIVE_OK` on Nick's instruction. Pilot preflight halts if the key
   file contains `POLYMARKET_PRIVATE_KEY` (owner key), lacks the session key, is group/other readable, the
   geoblock check fails, or trading approvals are missing.

Residual risk: a trade-only key can still lose money through bad trades; bounded by the $40 bot loss limit
(5-share orders, $5/match) and the $50 balance. Revoking the session key stops all trading at once.
