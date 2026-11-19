# Goalserve PM directories and clock — P15d0

Run: 2026-11-17 11:06:21Z

1. `find /mnt/HC_Volume_107257520 /vol2 -maxdepth 5 \( -name 'books.jsonl' -o -name 'books.jsonl.gz' -o -name 'markets.jsonl' -o -name 'markets.jsonl.gz' \) -printf '%h %f %s bytes %TY-%Tm-%TdT%TH:%TMZ\n' 2>/dev/null | sort | head -80`
```
/mnt/HC_Volume_107257520/pkarbs/cricket/2026-11-05 books.jsonl 3679962 bytes 2026-11-05T17:46Z
/mnt/HC_Volume_107257520/pkarbs/cricket/2026-11-05 markets.jsonl 661084 bytes 2026-11-05T17:45Z
/mnt/HC_Volume_107257520/pkarbs/cricket/2026-11-05/share books.jsonl 3679962 bytes 2026-11-05T17:46Z
/mnt/HC_Volume_107257520/pkarbs/cricket/2026-11-05/share markets.jsonl 661084 bytes 2026-11-05T17:46Z
/mnt/HC_Volume_107257520/pkarbs/dotacap/run-2026-11-16/out books.jsonl 55559486 bytes 2026-11-16T22:59Z
/mnt/HC_Volume_107257520/pkarbs/netflix books.jsonl.gz 0 bytes 2026-11-11T02:13Z
/mnt/HC_Volume_107257520/pkarbs/netflix/probe books.jsonl.gz 0 bytes 2026-11-11T05:45Z
/mnt/HC_Volume_107257520/pkarbs-ps-step2/winmodels/raw/dotacap-2026-11-04 books.jsonl.gz 3539319 bytes 2026-11-16T21:12Z
/mnt/HC_Volume_107257520/pkarbs-ps-step2/winmodels/raw/nbacap-2026-11-05-local2 books.jsonl.gz 263856 bytes 2026-11-16T21:12Z
/mnt/HC_Volume_107257520/pkarbs/scratch/ps-lead-20261115/aligned books.jsonl 528552299 bytes 2026-11-15T19:25Z
/mnt/HC_Volume_107257520/pkarbs/scratch/ps-lead-20261115/aligned markets.jsonl 30628 bytes 2026-11-15T19:22Z
/mnt/HC_Volume_107247271/pkarbs/scratch/ps-lead-20261115/pm books.jsonl 546983280 bytes 2026-11-15T19:20Z
/mnt/HC_Volume_107247271/pkarbs/scratch/ps-lead-20261115/pm books.jsonl.gz 63 bytes 2026-11-15T21:01Z
/mnt/HC_Volume_107247271/pkarbs/scratch/ps-lead-20261115/pm markets.jsonl 45931 bytes 2026-11-15T19:17Z
/mnt/HC_Volume_107247271/pkarbs/scratch/ps-lead-20261115/pm-window books.jsonl.gz 63 bytes 2026-11-15T21:25Z
/mnt/HC_Volume_107247271/pkarbs/scratch/ps-lead-20261115/pm-window markets.jsonl 56 bytes 2026-11-15T21:25Z
/mnt/HC_Volume_107247271/pkarbs/scratch/reexport_full markets.jsonl.gz 424977 bytes 2026-11-11T05:37Z
/mnt/HC_Volume_107247271/pkarbs/scratch/ts_manual_1794409049/files markets.jsonl.gz 476871 bytes 2026-11-11T15:09Z
/mnt/HC_Volume_107247271/pkarbs/tennis/2026-11-05 books.jsonl 1002747113 bytes 2026-11-05T21:10Z
/mnt/HC_Volume_107247271/pkarbs/tennis/2026-11-05 markets.jsonl 2760959 bytes 2026-11-05T21:06Z
/mnt/HC_Volume_107247271/pkarbs/tennis/2026-11-05/share books.jsonl 1002747113 bytes 2026-11-05T21:10Z
/mnt/HC_Volume_107247271/pkarbs/tennis/2026-11-05/share markets.jsonl 2760959 bytes 2026-11-05T21:06Z
/mnt/HC_Volume_107247271/pkarbs/thesports/final-topics-32295b books.jsonl 19170920814 bytes 2026-11-17T11:06Z
/mnt/HC_Volume_107247271/pkarbs/thesports/final-topics-32295b markets.jsonl 3094580 bytes 2026-11-17T11:01Z
/mnt/HC_Volume_107247271/pkarbs/thesports/final-topics-32295b/share books.jsonl.gz 3022979700 bytes 2026-11-17T10:51Z
/mnt/HC_Volume_107247271/pkarbs/thesports/final-topics-32295b/share markets.jsonl.gz 996202 bytes 2026-11-17T10:22Z
```
2. `ls -d /mnt/HC_Volume_107257520/pkarbs/goalserve/esports_payloads /mnt/HC_Volume_107257520/pkarbs/goalserve 2>&1`
```
/mnt/HC_Volume_107257520/pkarbs/goalserve
/mnt/HC_Volume_107257520/pkarbs/goalserve/esports_payloads
```
3. `ls /mnt/HC_Volume_107257520/pkarbs/goalserve | grep '^goalserve_2026111' | head`
```
goalserve_20261117.jsonl
```
4. `chronyc tracking` (host-name reference ID redacted under clause 13)
```
Reference ID    : <redacted>
Stratum         : 3
Ref time (UTC)  : Tue Nov 17 10:57:49 2026
System time     : 0.000011043 seconds slow of NTP time
Last offset     : +0.000032122 seconds
RMS offset      : +0.000120008 seconds
Frequency       : 2.919 ppm fast
Residual freq   : +0.000 ppm
Skew            : 0.019 ppm
Root delay      : 0.035507355 seconds
Root dispersion : 0.000815959 seconds
Update interval : 1031.4 seconds
Leap status     : Normal
```
5. `timedatectl` (machine-name field omitted under clause 13)
```
Local time: Tue 2026-11-17 11:06:22 UTC
Universal time: Tue 2026-11-17 11:06:22 UTC
RTC time: Tue 2026-11-17 11:06:22
Time zone: Etc/UTC (UTC, +0000)
System clock synchronized: yes
NTP service: active
RTC in local TZ: no
```

Requested line: The Polymarket recorder and Goalserve capture run on Prime. Prime's system clock is NTP-synchronized; chrony last offset was +0.000032122 seconds. This is a single-host clock reading, not a measured cross-machine offset.

No Nov 13–17 esports PM-books directory was identified under `/mnt/HC_Volume_107257520` in the bounded find. Older dated PM books found were in `/mnt/HC_Volume_107247271/pkarbs/scratch/ps-lead-20261115/`. The Goalserve payload listing contained `goalserve_20261117.jsonl` only. No files or processes changed.
