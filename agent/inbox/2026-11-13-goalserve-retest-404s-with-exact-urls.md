# To Hermes: retest the Goalserve 404s with exact URLs, and reconcile the WebSocket token result (13 Nov 2026, deadline 03:30Z)

Nick does not accept "404" without proof. Your status says basketball, cricket and esports return 404, but live/goalserve/capture.py never requests those URLs (it only polls tennis, soccer, baseball, hockey), and the earlier hard checks ran before the login was in the env file. Please re-run now, with the login and key as in capture.py, and write the results to agent/status/goalserve-probe.md.

Use the exact file names from Goalserve's documentation (https://inplay.goalserve.com/...):
- inplay-esports.gz (this one matters most: LoL Worlds final is 14 Nov)
- inplay-basket.gz (NOT "basketball")
- inplay-volleyball.gz
- inplay-amfootball.gz
- inplay-tennis.gz as the control that is known to work
Cricket: the docs list NO in-play odds file for cricket or rugby, so a 404 on inplay-cricket.gz is expected and is not a failure. Instead test the cricket livescore REST feed named in the Goalserve cricket documentation and report its URL path.

For EACH request write one row with: exact URL with user and key replaced by [R], HTTP status, body bytes after gunzip, first 200 characters of the body, and whether it was sent with the login+key query or without. Distinguish "404" from "200 with an empty list" (esports may be empty when no match is live, which is not the same as unavailable).

Also for the WebSocket token: at 02:19Z you wrote "WS token WORKS (JSON body)" and at 02:37Z you wrote "gettoken still 400 in every mapping". Say which is true. Paste the exact request form (method, URL, headers except secrets, JSON body keys only, key replaced by [R]) and the response status for the attempt that worked or failed.

Never write the key, login or server IP into any file. Post the probe within 30 min; if blocked, raise it to IT in agent/inbox at once.
