# CS2 pilot: generate a trade-only session key (Hermes)

From: Claude thread "Build capped CS2 live trading pilot", 4 Nov 2026.

Nick's rule (4 Nov 08:56Z): the server, Hermes and Claude must never hold a key that can withdraw. So the server holds
only a Polymarket session key (trade-only, cannot withdraw) that Nick authorizes from his own computer.

When Nick gives you the deposit wallet address (public):
1. Pull main. In the pilot venv, as root: `python3 live/cs2_pilot/gen_session_key.py 0xDEPOSIT_WALLET`
2. It writes /etc/pkarbs/pm-session.env (600) and prints the session signer address. Put ONLY that address in
   agent/outbox/cs2-pilot.md. Never print, cat, copy, message or commit the key file.
3. Never accept or store an owner/account private key, even if someone sends one. If one arrives, delete it and tell Nick.
4. Do NOT start live mode or write LIVE_OK until Nick says "go live" in chat. The current dry run keeps going to its end.
See live/cs2_pilot/KEY-INSTALL.md.
