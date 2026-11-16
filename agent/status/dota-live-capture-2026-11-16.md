# Dota live capture — update at 2026-11-16 08:38Z

## Result
- The approved capture is running as `dotacap-2026-11-16.service`; Node PID 1700948, 400 MiB cap, zero swap. It started 06:26:55Z, entered the scheduled window 08:30Z, and writes on VOL2.
- Installed the approved Prime crontab publisher. Recurring line: `*/30 * * * * /usr/bin/python3 /root/pkarbs/agent/tasks/dota-live-capture-2026-11-16-publish.py >> /vol2/pkarbs/dotacap/run-2026-11-16/publisher/cron.log 2>&1`. A one-shot final copy at 17 Nov 20:35Z removes both publisher entries afterwards.
- Six manual publisher runs have succeeded; each shipped complete new JSONL lines as gzip deltas, checksum-verified storage-box copies, and pushed the corresponding manifest. Latest manifest commit: `b0fa494b0f3a126731e88c9a2c0262867dcb50b9`; manifest path `manifest/dotacap-2026-11-16.tsv`, 28 entries/files confirmed on the box. No raw data was committed.
- At 08:37Z, service remained active at about 65 MiB under the 400 MiB cap, with output growing. Feed coverage/final pass-fail is not established.

## Implementation and revert
- Publisher `agent/tasks/dota-live-capture-2026-11-16-publish.py`, SHA-256 `e6c046b10b179ae940b6d9c96e29f0a1904709f14f4355f2a5e9a27f3e467476`; `py_compile` passed. State and runtime chunks/logs stay on VOL2; credentials are read at runtime and not printed.
- Revert: remove crontab lines containing `dotacap-publisher-2026-11-16`; capture is unaffected. Keep the script until both lines are removed.
- First manifest commit `3038c9d59156437c64692a38ca43a6125a2eff71`; latest `b0fa494b0f3a126731e88c9a2c0262867dcb50b9`.
