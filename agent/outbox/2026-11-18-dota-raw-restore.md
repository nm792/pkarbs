APPROVALS NEEDED: none
RESULT
- R1: six local capture files, 603,741 rows total; R2: 75 current chunks (49,194,725 bytes). The 75 historical manifest names are distinct from current chunks because shipped chunks are unlinked.
- R3: storage-box listing has 75 files (15,650,708 bytes); all 75 manifest SHA-256 checks passed against a temporary read-only copy. R4 was correctly skipped because R1–R3 did not all fail.
- P28b: lag analysis rerun completed from R1 using the fetched capture-specific config; 19 Valve match records, 11 price-paired, 38 timed event lags, median 295.25 s, mean cross-correlation peak −285 s. No <60 s finding.
- Verification run: 2,000 MiB cap, 22.95 s, exit 0, peak RSS 1,642,256 KiB. The earlier 1,500 MiB attempt was OOM-killed.
DATA
- P28a evidence: `agent/status/dota-raw-restore-2026-11-18.md`
- P28b result: `winmodels/dota/livelag/out_lag_2026-11-16.json`, `.txt`
OPEN / NOT VERIFIED
- none
Count: notes run 2, outstanding 0, PENDING open 0
