## AAA watch (19 Nov)

- Source commit: `71bd42c3`.
- SHA-1: `aaa_watch.py` `94cab973c2055a7b3a03422f1c79613313b517d1`; `test_aaa_watch.py` `585ed9b380962e88acbefcf61a556b9e7189c6a0`.
- Tests: `3 of 3 tests pass`.
- Scheduled watcher process launched at 05:45Z, PID 2879168; start is delayed until 07:28Z and ends at 09:00Z (max 5400 seconds; 5-second interval). It writes under `/mnt/HC_Volume_107257520/gas_watch`, not root.
- At 05:45Z the delayed process was alive; output files do not yet exist because the watcher has not started. HTTP status codes and the first three JSONL lines are therefore not yet available.


## PMXT archive listing (19 Nov)

- Checked at 06:54Z per P55a.
- `curl -sS -m 60` timed out before receiving a response: HTTP 000, 0 bytes; curl error 28, connection timed out after 60001 ms.
- No listing body was received; the requested first 4000 bytes are unavailable. No archive listing file was created.
