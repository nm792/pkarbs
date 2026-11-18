# P33 PandaScore Dota inventory — 2026-11-18

Read-only inventory on Prime. No interpretation or live state change. The command output below omits infrastructure path identifiers and redacts token IDs.

## PandaScore raw directory

```text
first filename: pandascore_2026111612.jsonl.gz
last filename: pandascore_2026111819.jsonl.gz
file count: 4
`du -sb`: 2303383 bytes
```

## Requested books files

Requested file A (the mounted-volume `pkarbs/share/books.jsonl.gz` path) was absent:

```text
ls: cannot access [requested file A]: No such file or directory
zcat: [requested file A]: No such file or directory (first and last line checks)
```

Requested file B (`/vol2/pkarbs/dotacap/run-2026-11-16/out/books.jsonl`):

```text
-rw-r--r-- 1 root root 55559486 2026-11-16T22:59:59Z [requested file B]
first: {"recv_ms":1794818700550,"label":"dota2-angryb-lynx-2026-11-16","q":"Dota 2: angry birds vs Team Lynx - Game 1 Winner","outcome":"angry birds","token":"[redacted]","bid":0.61,"ask":0.62,...}
last: {"recv_ms":1794869999590,"label":"dota2-legion1-aur1-2026-11-16","q":"Dota 2: LEGION vs Aurora (BO3) - 1win Essence Playoffs","outcome":"LEGION","token":"[redacted]","bid":0.36,"ask":0.38,...}
```

The terminal output masked the token IDs; no token value is reported. The displayed line samples are abbreviated after the quoted top-of-book fields.

## Disk

```text
Filesystem        1B-blocks        Used   Available Use% Mounted on
[redacted]       105089261568 79192715264 20511059968  80% [requested volume]
[redacted]       105089261568 79192715264 20511059968  80% [same filesystem]
```

The two `df` arguments resolved to the same filesystem in the returned output.
