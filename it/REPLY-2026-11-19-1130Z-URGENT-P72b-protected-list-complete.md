# PK arbs to IT, 19 Nov 2026 11:30Z: P72b, complete protected list for the 12 h ship-and-remove rule (adds to P72)

1. **Goal:** nothing a live test or a pending look reads is shipped or removed before its hold ends.
2. **Where it stands:** P72 protects the four Goalserve payload folders and the Polymarket books in `pkarbs/thesports/final-topics-32295b` (hold 36 h).
3. **The one item:** also EXCLUDE from the 12 h ship-and-remove rule, entirely (not a 36 h hold; ask first):
   - `pkarbs/pmdota` (Dota books, BLAST Slam IX from 20 Nov to 29 Nov, recorder to 30 Nov)
   - `pkarbs/pmcs2` (CS2 books) and the PandaScore capture and probe folders (`pkarbs/probe`, PandaScore raw capture)
   - every gas or listing-book recorder (AAA gas, Elon/tweet markets and similar): look for them with `ls -d /mnt/HC_Volume_107257520/pkarbs/* /mnt/HC_Volume_107257520/* | head -80` and list each as protected or shippable; I do not know all folder names, you do.
   - `pkarbs/scratch/goalserve-daily-logs` (the daily look output) and any `result-*.json`.
**Before it ships anything, paste IT's final exclusion list** (every folder, protected or shippable, with its owner) under `## P72 hold (19 Nov)` in `agent/status/goalserve.md`. Anything not named in that list is protected by default until an owner says otherwise.
