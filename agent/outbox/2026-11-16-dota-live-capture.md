# Dota live capture — status at 2026-11-16 07:33Z

The existing capture is active as `dotacap-2026-11-16.service` (Node PID 1700948; timeout PID 1700947), started 06:26:55Z with a 400 MiB memory cap and zero swap. Its output is on the data volume. The capture window begins 08:30Z and ends 2026-11-17 20:30Z; at 07:32Z its only output was `capture.log` (192 bytes), stating NTP synchronized and waiting until 08:30Z. No match or book data has been collected yet.

The approved 30-minute gzip/push publisher is not installed. The Prime crontab has no Dota publisher line. This scheduled run's delivery instruction prohibits creating or updating cron jobs, so I did not install the requested no-model cron line. Consequently, the capture output will not be copied to `winmodels/raw/dotacap-2026-11-16/` by a recurring publisher in this run. I made no code/config changes and did not alter the running capture.

The live service was confirmed active at 07:32Z. No feed reachability or capture pass result is available before the 08:30Z window.
