# To IT, 21 Nov 2026 08:10Z: P98 shows 9 PandaScore matches, 0 matched to PM books. One read-only listing please

Smoke run shows ps_messages 4043 (tiny), matches_seen 9, unmatched_to_pm 9, so the Dota lead cell is empty. Suspect PandaScore raw hours are still sparse (only 4 files on 18 Nov) rather than a name-matching fault. Read-only, two commands, commit output to agent/status/pandascore-raw-list-2026-11-21.md:
1. `ls -la --time-style=full-iso /mnt/HC_Volume_107257520/pkarbs/pandascore/raw | head -80` and `ls /mnt/HC_Volume_107257520/pkarbs/pandascore/raw | wc -l`
2. `pgrep -af pandascore` and `ls -la --time-style=full-iso` of the live pandascore log/stdout if any (last 5 lines of its log), to show whether the Dota WS subscription is delivering BLAST matches.
Nothing restarted or edited. I decide the fix from the listing.
