# 00-URGENT (Nick 20 Nov 03:23Z, "sample, don't build"): export 3 recent CS2 matches, READ-ONLY. Do before anything else of mine.
git fetch origin reviewer; git checkout origin/reviewer -- it/
V=/mnt/HC_Volume_107257520/pkarbs/pandascore/raw   # if hour files were shipped to the storage box, point RAW at the box copy
mkdir -p /root/ps_samples && python3 -I it/ps_export_samples.py $V /root/ps_samples 3
cp /root/ps_samples/ps_sample_* /root/pkarbs/scratch/ps_samples/   # create dir; a few MB gz
Commit ONLY those files to branch `reviewer` under scratch/ps_samples/ (add, no deletions) and paste the printed index (match ids, message counts, inround_messages, bytes) to agent/status/pandascore.md.
If inround_messages is 0 for every match, say so in the paste: that answers Nick's "are the new fields captured" with NO for those files.
