APPROVALS NEEDED:
- None. No copy, delete, cron or process change was made; the 36 h capacity gate failed.

RESULT
- VOL2 free space was 21,110,800,384 bytes at 11:57:12Z and 19,737,276,416 bytes at 12:09:09Z. Largest top-level directories at the final inventory: `pkarbs` 68,685,848,576 bytes; `pkarbs-ps-step2` 3,412,783,104; `asx` 1,250,680,832; `nt_live_fire` 1,192,034,304; `mfw-ct` 734,187,520. Within `pkarbs`: `thesports` 52,040,945,664; `scratch` 7,639,179,264; `from-vol` 6,827,454,464; `goalserve` 1,053,659,136; `dotacap` 452,657,152; `pmcs2` 199,901,184 bytes.
- Two `final-topics-32295b` readings: 50,831,223,158 bytes at 11:57:12Z and 52,152,370,706 bytes at 12:09:09Z (697 seconds); growth about 6.82 GB/hour, or 245.4 GB over 36 h. The earlier 10-minute pair (11:57:12Z to 12:06:35Z) measured about 6.59 GB/hour; both are far above available headroom. A subsequent read at 12:11:11Z found the tree at 48,421,855,232 bytes, showing active files can roll over and `du` totals are non-monotone; use the measured short-window growth only as an indicative rate, not an exact forecast. VOL2 free at 12:11:11Z was 23,455,006,720 bytes (13.46 GB above the 10 GB floor). Even this headroom is far below the measured ~6.6–6.8 GB/hour rate for 36 hours.
- Capacity condition fails; no data was shipped/deleted and no crontab line was added or run. The 12:11:11Z top-level inventory showed VOL2: pkarbs 61,544,989,448 bytes; pkarbs-ps-step2 2,278,912,232; swapfile2 2,147,483,648; asx 1,250,064,461; nt_live_fire 1,190,626,704; mfw-ct 722,850,174; mfw-lc-5c486e01 591,717,919 bytes. Within pkarbs: thesports 48,426,769,537; scratch 6,349,023,184; from-vol 4,558,674,094; goalserve 1,065,752,130; dotacap 452,228,532; pmcs2 203,566,428 bytes. A complete exclusion/hold list is in `agent/status/goalserve.md` under `P72 hold (19 Nov)`.

DATA
- Live disk and directory measurements are summarized above; the list of top-level folders and active process checks was taken on Prime at 11:56–12:09Z.

OPEN / NOT VERIFIED
- P72 requires PK arbs to provide a filter before shipping can proceed; no storage-box transfer was attempted.

Count: notes run 1, outstanding 1, PENDING open 0
