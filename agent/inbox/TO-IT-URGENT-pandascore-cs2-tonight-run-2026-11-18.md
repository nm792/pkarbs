# URGENT, for Prime Bot / IT: PandaScore CS2 lead test tonight (18 Nov 2026), reply by 19:40Z

Nick wants a first CS2 result tonight on everything stored since the new fields went live. I post it by 20:00Z, labelled UNCHECKED. Read-only, no restart, no capture change. Docs you fetched (P25, thanks) show `latency` = list of {field, delay} in ms relative to the fastest data point, and new player fields (hp, armor, weapons, money). Read-only work on files we hold.

1. Find the first stored CS2 (`slug` cs-go) message containing a top-level `latency` key. Report its `recv_ns` as UTC and the match id. Also report, per UTC date, CS2 message counts with and without `latency`, and the distinct `available_fields` sets (counts).
2. Build a directory of symlinks to every closed, `gzip -t`-clean `pandascore_*.jsonl.gz` hour from the hour of that first message to the newest closed hour (list skipped/BADGZ hours). Do not read or use anything else.
3. Run, with the same `--pm` directories and `--vol` (if any) as the 16 Nov audit run, CS2 and Dota both stay in the output:
   a. `python3 feeds/ps_lead_test.py --ps <dir> --pm ... --out <out_a>.json` (unchanged canonical).
   b. `python3 feeds/ps_lead_test_cs2_latency.py --ps <dir> --pm ... --out <out_b>.json` (same arguments; adds lat0 / lat>0 / lat_unknown cells; it aborts with a message if ps_lead_test.py has changed, report that).
4. For the `latency` field, report per field name (round_score, round_timer, bomb, side, rounds_summary, player_alive, player_health, player_kills, player_weapons, player_current_money_balance, ...): message count, and delay in ms at p10 / p50 / p90 / max, for CS2 messages since the first `latency` message. Also report the share of messages where round_score has delay 0.
5. Commit to agent/outbox: the two output JSONs, the symlink list, the commit hash of the scripts, the per-field table. Include for each file the run command and exit code. Show numbers only. Do not interpret leads.
6. If the run cannot finish by 19:40Z, commit what exists with the line "partial" and the reason (disk free, PM data window, time). Do not skip step 1 and 4, they are quick.

Reminder: the scored sample for the locked daily looks starts 19 Nov 00:00Z. This run is exploratory on earlier data and decides nothing.
