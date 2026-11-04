# CS2 pilot: generate a trade-only session key (Hermes)

From: Claude thread "Build capped CS2 live trading pilot", 4 Nov 2026.

Nick's rule (4 Nov 08:56Z): the server, Hermes and Claude must never hold a key that can withdraw. So the server holds
only a Polymarket session key (trade-only, cannot withdraw) that Nick authorizes from his own computer.

Nick gave the deposit wallet address in chat 4 Nov 09:03Z: **0x8A5D1798f2A82DBB6Bd8B961f91f303EbBe5eaC7**. DO THIS NOW:
1. Pull the default branch (claude/project-thread-vg2ckg). In the pilot venv (it has eth_account via polymarket-client), as root: `python3 live/cs2_pilot/gen_session_key.py 0x8A5D1798f2A82DBB6Bd8B961f91f303EbBe5eaC7`
2. It writes /etc/pkarbs/pm-session.env (600) and prints the session signer address. Put ONLY that address in
   agent/outbox/cs2-pilot.md. Never print, cat, copy, message or commit the key file.
3. Never accept or store an owner/account private key, even if someone sends one. If one arrives, delete it and tell Nick.
4. Do NOT start live mode or write LIVE_OK until Nick says "go live" in chat. The current dry run keeps going to its end.
See live/cs2_pilot/KEY-INSTALL.md.
