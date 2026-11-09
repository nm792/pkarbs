# thesports-recorder-stopped-2026-11-07 (status, 11:07T21:56Z)

TheSports live recorder is DOWN. Clean `stop` at ~16:00:13Z (log tail shows mqtt "Normal disconnection" then stop; counts books 1,412,988 / ts_mqtt 528,438 / pmws 13,156). capture.py not running; no unit/tmux/cron guard. Fresh books.jsonl sat ~6h (last 16:00:08Z). Only chunk final-topics-32295 present.

One-line ask (consent-gated): restart live/thesports/capture.py from the volume chunk dir (resumes the trial over the CS2/LoL Worlds 7-8 Nov window); approve to relaunch, or say the capture window is intended closed and the overflow will be back-filled differently.
