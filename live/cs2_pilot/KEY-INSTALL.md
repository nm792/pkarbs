# Trading key for the CS2 pilot: WITHDRAWN plan, see rule below

**Rule (Nick, 4 Nov 2026 08:56Z): neither Claude nor Hermes nor the server may ever hold a key that can withdraw or
drain the account.** The earlier version of this file (owner private key in /etc/pkarbs on the server) breaks that
rule and must not be used. Do not put any account/owner private key on the server.

## Planned design (not built yet; waiting for Nick's go-ahead)
Polymarket Session Keys (docs: /trading/session-keys, beta): "A Session Key is a separate signer that a Deposit
Wallet Owner authorizes to trade for a Deposit Wallet ... A Session Key cannot withdraw funds from the Deposit Wallet."
1. Hermes generates a fresh session keypair on the server and publishes only its address.
2. Nick authorizes that address from his own computer with his owner key (CLOB scope, expiry <= 180 days); the owner
   key never leaves his machine. Revocable at any time.
3. The pilot signs orders with the session key only.
Prerequisites: a Deposit Wallet account (new accounts), a Builder API key (polymarket.com > Settings > API Keys), and,
during the beta, session-key management enabled on that Builder key by builder@polymarket.com.
Residual risk: a trade-only key can still lose money through bad trades; bounded by the $40 bot loss limit and the $50 balance.
