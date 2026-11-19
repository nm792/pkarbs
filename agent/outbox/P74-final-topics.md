## P68 thesports folder (19 Nov)

Read-only identification, measured 14:04Z; nothing shipped or deleted and no process stopped.

```text
Largest entries under /mnt/HC_Volume_107257520/pkarbs/thesports (8 requested):
49G /mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b
Only one immediate entry was present.

Last six lines of final-topics-32295b:
-rw-r--r-- 1 root root 74267986 2026-11-19 14:04:28.109232146 +0000 pmws.jsonl
drwxr-xr-x 2 root root 4096 2026-11-19 13:32:43.236690855 +0000 share
-rw-r--r-- 1 root root 1022747801 2026-11-19 14:04:20.994215794 +0000 trades.jsonl
-rw-r--r-- 1 root root 211024 2026-11-19 14:04:21.569217116 +0000 trades.watermark.json
-rw-r--r-- 1 root root 17088904344 2026-11-19 10:11:12.992746190 +0000 ts_mqtt.jsonl
-rw-r--r-- 1 root root 57645071 2026-11-19 10:11:14.239742426 +0000 ts_poll.jsonl

Processes (command lines truncated to 160 chars):
root 3243759 2.8 0.4 53016 38956 ? Ss 10:11 6:32 /usr/bin/python3 -I /root/pkarbs/live/thesports/pm_trades_capture.py /mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b --interval 30
root 3243761 84.4 2.2 570484 179932 ? Ssl 10:11 196:59 /usr/bin/python3 -I /root/pkarbs/live/thesports/capture.py /mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b 160 --share /mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b/share
root 3543459 0.0 0.0 2888 1816 ? Ss 14:00 0:00 /bin/sh -c bash /root/pkarbs/live/thesports/export_timer_2h.sh >> /var/log/thesports_export_timer.log 2>&1
root 3543479 0.0 0.0 7668 2312 ? S 14:00 0:00 bash /root/pkarbs/live/thesports/export_timer_2h.sh
root 3559437 56.8 45.3 3632652 3599044 ? R 14:02 1:05 /usr/bin/python3 /root/pkarbs/live/thesports/export_slim_32295_plumb.py /mnt/HC_Volume_107257
```

Units `thesports-capture-b.service` (PID 3243761) and `thesports-pmtrades.service` (PID 3243759) were active at 14:04Z. The live `capture.py` writes `books.jsonl` and `markets.jsonl` alongside `ts_mqtt.jsonl`, `ts_poll.jsonl`, `pmws.jsonl`, and `log.jsonl`; the trade-capture writes `trades.jsonl`. A 14:05Z stat showed books and trades still growing. Per this row, nothing was stopped and no files were shipped or removed.

## P74 final-topics profile (19 Nov)

Reviewer profile script `it/pm_folder_stats.py` was run at 14:04Z. It reported 16 files, 52,426,205,554 bytes at that instant; a follow-up `du -sb` at 14:06:57Z measured 52,675,757,561 bytes (actively growing).

```text
folder /mnt/HC_Volume_107257520/pkarbs/thesports/final-topics-32295b 2026-11-19T14:04:43Z
files 16 total_bytes 52426205554
     24996748464  11-19 14:04:43  books.jsonl
     17088904344  11-19 10:11:12  ts_mqtt.jsonl
      3946496727  11-19 13:09:54  share/books.jsonl.gz
      3331064388  11-19 14:04:43  share/books.jsonl.gz.tmp
      1762545643  11-19 13:32:13  share/ts_mqtt.jsonl.gz
      1022747801  11-19 14:04:20  trades.jsonl
       136475414  11-19 13:32:42  share/trades.jsonl.gz
        74267986  11-19 14:04:28  pmws.jsonl
        57645071  11-19 10:11:14  ts_poll.jsonl
         3798294  11-19 14:02:08  markets.jsonl
         2792807  11-19 13:32:16  share/pmws.jsonl.gz
         1228624  11-19 13:32:14  share/markets.jsonl.gz
          719496  11-19 13:32:14  share/ts_poll.jsonl.gz
          507554  11-19 14:04:30  log.jsonl
          211024  11-19 14:04:21  trades.watermark.json
           51917  11-19 13:32:43  share/log.jsonl.gz
markets file markets.jsonl rows 6766 keys {'ms': 6766, 'sport': 6766, 'slug': 6766, 'gid': 6766, 'title': 6766, 'start': 6766, 'question': 6766, 'smt': 6766, 'cond': 6766, 'tokens': 6766, 'outcomes': 6766}
markets by sport {'tennis': 4607, 'cs2': 1268, 'dota2': 598, 'cricket': 132, 'nba': 89, 'nfl': 27, 'lol': 45}
books file books.jsonl tail_MB 20.0 row keys {'ms': 21395, 'sent': 21395, 'tk': 21395, 'ts': 21395, 'bids': 21395, 'asks': 21395}
  bytes share by sport (last 20.0 MB): {'tennis': '57.7%', 'cs2': '25.1%', 'dota2': '13.5%', 'cricket': '3.6%'}
  rows by sport: {'tennis': 13035, 'cs2': 5128, 'dota2': 2572, 'cricket': 660}
```

The supplied book-profile script exited 1 after printing those book statistics (`AttributeError: 'int' object has no attribute 'keys'`) while processing a non-object JSON value. An independent bounded 20 MB tail read completed: 22,298 rows, 1 malformed/truncated JSON line, 0 non-object values; mapped bytes by sport were tennis 57.4%, CS2 25.1%, Dota2 13.8%, cricket 3.7% (22,298 rows). This read-only fallback confirms non-look bytes are not all disposable; it does not authorize any change to books or markets.

Stopgap check: no eligible non-look regular file older than 6 hours was present at 14:06Z. None shipped or removed; the storage-box top-level listing showed the `pkarbs-capture` destination exists. The two live writers remain active. No restart/stop was performed.
