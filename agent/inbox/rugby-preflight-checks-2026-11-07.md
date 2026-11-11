# Rugby AB preflight: three extra checks (project thread, 7 Nov 09:20Z)

Thanks for the ack. Nick asked us to double-check readiness. Code compiles and the config times match gamma. Three things to verify at the 12:30Z preflight, and write the results to agent/status/rugby-top14-capture.md:

1. **ESPN scoreboard 270559 status from the server with the harness UA.** From the project sandbox the same URL returned 403 with the UA `pkarbs-research/1.0 (contact nm@delphic.co)` and 200 with a shorter UA, so it may be a UA filter. If the server gets 403, keep the honest UA but drop the email in parentheses, and say so in the log. Rugbyrama widget (61242) and CLOB REST returned 200 here.
2. **Timeout arithmetic.** `run_for` counts from process start. Start no later than 13:10Z so AB covers kickoff-15 min (13:15Z) to the last kickoff 15:35Z + 2.5 h = 18:05Z. 18000 s from 13:10Z ends 18:10Z, which is fine; a later start loses the tail.
3. **Pau v Perpignan listing.** ESPN lists a "PERPI VS SECTI" fixture at 15:30Z and "SEC VS USA" at 15:35Z, both of which look like the same match. Log both event ids in the first ESPN poll so the analysis can match them to the gamma ticker rutopft-pau-per-2026-11-07.

Also: status file agent/status/rugby-top14-capture.md still says PREPARED from 2 Nov; update it at start so the thread can see the run is live.
