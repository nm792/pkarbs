# P98 — Dota lead smoke, 2026-11-20

Read-only run from a clean `git archive` export of `origin/claude/project-thread-vg2ckg`; no source edits, process restarts, or data deletions.

## Run
- Script: committed `feeds/run_dota_lead.sh`; exit code: 0.
- Inputs: PandaScore raw and Polymarket Dota recorder data on VOL2; output: `scratch/dota-lead-2026-11-20/` on VOL2.
- Summary:
```text
ps_messages 4043 events 161 matches_seen 9 unmatched_to_pm 9
dota2|map|all n_events 0 n_with_onset 0 n_matches 0 onset% None median_real None median_placebo None diff None ci None after% None verdict UNKNOWN (n_matches<12 or n_with_onset<30)
dota2|match|all n_events 0 n_with_onset 0 n_matches 0 onset% None median_real None median_placebo None diff None ci None after% None verdict UNKNOWN (n_matches<12 or n_with_onset<30)
```

## result.json
```json
{
  "cells": {
    "cs2|map|all": {
      "ci95_match_boot": null,
      "diff_s": null,
      "median_placebo_lead_s": null,
      "median_real_lead_s": null,
      "n_events": 0,
      "n_matches": 0,
      "n_placebo": 0,
      "n_placebo_with_onset": 0,
      "n_with_onset": 0,
      "pct_placebo_after": null,
      "pct_placebo_with_onset": null,
      "pct_price_after_feed": null,
      "pct_real_with_onset": null,
      "verdict": "unknown (n=0 < 30), preliminary"
    },
    "cs2|match|all": {
      "ci95_match_boot": null,
      "diff_s": null,
      "median_placebo_lead_s": null,
      "median_real_lead_s": null,
      "n_events": 0,
      "n_matches": 0,
      "n_placebo": 0,
      "n_placebo_with_onset": 0,
      "n_with_onset": 0,
      "pct_placebo_after": null,
      "pct_placebo_with_onset": null,
      "pct_price_after_feed": null,
      "pct_real_with_onset": null,
      "verdict": "unknown (n=0 < 30), preliminary"
    },
    "dota2|map|all": {
      "ci95_match_boot": null,
      "diff_s": null,
      "median_placebo_lead_s": null,
      "median_real_lead_s": null,
      "n_events": 0,
      "n_matches": 0,
      "n_placebo": 0,
      "n_placebo_with_onset": 0,
      "n_with_onset": 0,
      "pct_placebo_after": null,
      "pct_placebo_with_onset": null,
      "pct_price_after_feed": null,
      "pct_real_with_onset": null,
      "verdict": "unknown (n=0 < 30), preliminary"
    },
    "dota2|match|all": {
      "ci95_match_boot": null,
      "diff_s": null,
      "median_placebo_lead_s": null,
      "median_real_lead_s": null,
      "n_events": 0,
      "n_matches": 0,
      "n_placebo": 0,
      "n_placebo_with_onset": 0,
      "n_with_onset": 0,
      "pct_placebo_after": null,
      "pct_placebo_with_onset": null,
      "pct_price_after_feed": null,
      "pct_real_with_onset": null,
      "verdict": "unknown (n=0 < 30), preliminary"
    }
  },
  "events_without_market": {
    "('cs2', 'Map 1 Winner')": 82,
    "('cs2', 'Map 2 Winner')": 15,
    "('cs2', 'Match Winner')": 97,
    "('dota2', 'Map 1 Winner')": 64,
    "('dota2', 'Match Winner')": 64
  },
  "ps_events_total": 161,
  "ps_matches_seen": 9,
  "ps_matches_unmatched_to_pm": 9,
  "ps_messages": 4043,
  "seed": 20261115,
  "strata_computed": false
}
```

## audit.json
```json
{
  "A_gap_buckets": {
    "cs2|map|gap 0-10s": {
      "median_real_lead_s": null,
      "n_events": 0,
      "n_with_onset": 0,
      "pct_price_after_feed": null
    },
    "cs2|map|gap 10-30s": {
      "median_real_lead_s": null,
      "n_events": 0,
      "n_with_onset": 0,
      "pct_price_after_feed": null
    },
    "cs2|map|gap 30-60s": {
      "median_real_lead_s": null,
      "n_events": 0,
      "n_with_onset": 0,
      "pct_price_after_feed": null
    },
    "cs2|map|gap 60-infs": {
      "median_real_lead_s": null,
      "n_events": 0,
      "n_with_onset": 0,
      "pct_price_after_feed": null
    },
    "cs2|match|gap 0-10s": {
      "median_real_lead_s": null,
      "n_events": 0,
      "n_with_onset": 0,
      "pct_price_after_feed": null
    },
    "cs2|match|gap 10-30s": {
      "median_real_lead_s": null,
      "n_events": 0,
      "n_with_onset": 0,
      "pct_price_after_feed": null
    },
    "cs2|match|gap 30-60s": {
      "median_real_lead_s": null,
      "n_events": 0,
      "n_with_onset": 0,
      "pct_price_after_feed": null
    },
    "cs2|match|gap 60-infs": {
      "median_real_lead_s": null,
      "n_events": 0,
      "n_with_onset": 0,
      "pct_price_after_feed": null
    },
    "dota2|map|gap 0-10s": {
      "median_real_lead_s": null,
      "n_events": 0,
      "n_with_onset": 0,
      "pct_price_after_feed": null
    },
    "dota2|map|gap 10-30s": {
      "median_real_lead_s": null,
      "n_events": 0,
      "n_with_onset": 0,
      "pct_price_after_feed": null
    },
    "dota2|map|gap 30-60s": {
      "median_real_lead_s": null,
      "n_events": 0,
      "n_with_onset": 0,
      "pct_price_after_feed": null
    },
    "dota2|map|gap 60-infs": {
      "median_real_lead_s": null,
      "n_events": 0,
      "n_with_onset": 0,
      "pct_price_after_feed": null
    },
    "dota2|match|gap 0-10s": {
      "median_real_lead_s": null,
      "n_events": 0,
      "n_with_onset": 0,
      "pct_price_after_feed": null
    },
    "dota2|match|gap 10-30s": {
      "median_real_lead_s": null,
      "n_events": 0,
      "n_with_onset": 0,
      "pct_price_after_feed": null
    },
    "dota2|match|gap 30-60s": {
      "median_real_lead_s": null,
      "n_events": 0,
      "n_with_onset": 0,
      "pct_price_after_feed": null
    },
    "dota2|match|gap 60-infs": {
      "median_real_lead_s": null,
      "n_events": 0,
      "n_with_onset": 0,
      "pct_price_after_feed": null
    }
  },
  "A_isolated": {
    "cs2|map|all_events": {
      "audit_word": "unknown (n<30)",
      "ci95": null,
      "diff_s": null,
      "median_placebo_lead_s": null,
      "median_real_lead_s": null,
      "n_events": 0,
      "n_matches": 0,
      "pct_placebo_with_onset": null,
      "pct_price_after_feed": null,
      "pct_real_with_onset": null
    },
    "cs2|map|isolated_gap>=60s": {
      "audit_word": "unknown (n<30)",
      "ci95": null,
      "diff_s": null,
      "median_placebo_lead_s": null,
      "median_real_lead_s": null,
      "n_events": 0,
      "n_matches": 0,
      "pct_placebo_with_onset": null,
      "pct_price_after_feed": null,
      "pct_real_with_onset": null
    },
    "cs2|match|all_events": {
      "audit_word": "unknown (n<30)",
      "ci95": null,
      "diff_s": null,
      "median_placebo_lead_s": null,
      "median_real_lead_s": null,
      "n_events": 0,
      "n_matches": 0,
      "pct_placebo_with_onset": null,
      "pct_price_after_feed": null,
      "pct_real_with_onset": null
    },
    "cs2|match|isolated_gap>=60s": {
      "audit_word": "unknown (n<30)",
      "ci95": null,
      "diff_s": null,
      "median_placebo_lead_s": null,
      "median_real_lead_s": null,
      "n_events": 0,
      "n_matches": 0,
      "pct_placebo_with_onset": null,
      "pct_price_after_feed": null,
      "pct_real_with_onset": null
    },
    "dota2|map|all_events": {
      "audit_word": "unknown (n<30)",
      "ci95": null,
      "diff_s": null,
      "median_placebo_lead_s": null,
      "median_real_lead_s": null,
      "n_events": 0,
      "n_matches": 0,
      "pct_placebo_with_onset": null,
      "pct_price_after_feed": null,
      "pct_real_with_onset": null
    },
    "dota2|map|isolated_gap>=60s": {
      "audit_word": "unknown (n<30)",
      "ci95": null,
      "diff_s": null,
      "median_placebo_lead_s": null,
      "median_real_lead_s": null,
      "n_events": 0,
      "n_matches": 0,
      "pct_placebo_with_onset": null,
      "pct_price_after_feed": null,
      "pct_real_with_onset": null
    },
    "dota2|match|all_events": {
      "audit_word": "unknown (n<30)",
      "ci95": null,
      "diff_s": null,
      "median_placebo_lead_s": null,
      "median_real_lead_s": null,
      "n_events": 0,
      "n_matches": 0,
      "pct_placebo_with_onset": null,
      "pct_price_after_feed": null,
      "pct_real_with_onset": null
    },
    "dota2|match|isolated_gap>=60s": {
      "audit_word": "unknown (n<30)",
      "ci95": null,
      "diff_s": null,
      "median_placebo_lead_s": null,
      "median_real_lead_s": null,
      "n_events": 0,
      "n_matches": 0,
      "pct_placebo_with_onset": null,
      "pct_price_after_feed": null,
      "pct_real_with_onset": null
    }
  },
  "B_reconciliation": {
    "per_match": {
      "1789186": {
        "any_change": {
          "round": 15
        },
        "increases": {
          "round": 15
        }
      },
      "1791313": {
        "any_change": {
          "round": 8
        },
        "increases": {
          "round": 8
        }
      },
      "1791816": {
        "any_change": {
          "barracks": 6,
          "kills": 25,
          "roshans": 2,
          "towers": 11
        },
        "increases": {
          "barracks": 6,
          "kills": 25,
          "roshans": 2,
          "towers": 11
        }
      },
      "1793342": {
        "any_change": {
          "barracks": 2,
          "kills": 13,
          "roshans": 1,
          "towers": 4
        },
        "increases": {
          "barracks": 2,
          "kills": 13,
          "roshans": 1,
          "towers": 4
        }
      },
      "1796498": {
        "any_change": {
          "round": 9
        },
        "increases": {
          "round": 9
        }
      },
      "1796514": {
        "any_change": {
          "round": 16
        },
        "increases": {
          "round": 16
        }
      },
      "1803639": {
        "any_change": {
          "round": 12
        },
        "increases": {
          "round": 12
        }
      },
      "1805736": {
        "any_change": {
          "round": 37
        },
        "increases": {
          "round": 37
        }
      }
    },
    "totals_any_change": {
      "barracks": 8,
      "kills": 38,
      "roshans": 3,
      "round": 97,
      "towers": 15
    },
    "totals_increases": {
      "barracks": 8,
      "kills": 38,
      "roshans": 3,
      "round": 97,
      "towers": 15
    }
  },
  "C_unmatched": {
    "1789186": {
      "pm_markets_sharing_a_name_token": [],
      "ps_events": 15,
      "ps_names": [
        "genone",
        "leo team"
      ],
      "title": "cs2"
    },
    "1791313": {
      "pm_markets_sharing_a_name_token": [],
      "ps_events": 8,
      "ps_names": [
        "luminosity",
        "sangal"
      ],
      "title": "cs2"
    },
    "1791816": {
      "pm_markets_sharing_a_name_token": [
        {
          "kind": "Map 1 Winner",
          "outcomes": [
            "CyberHero",
            "HULIGANI"
          ],
          "q": "Dota 2: CyberHero vs HULIGANI - Game 1 Winner"
        },
        {
          "kind": "Map 2 Winner",
          "outcomes": [
            "CyberHero",
            "HULIGANI"
          ],
          "q": "Dota 2: CyberHero vs HULIGANI - Game 2 Winner"
        },
        {
          "kind": "Match Winner",
          "outcomes": [
            "CyberHero",
            "HULIGANI"
          ],
          "q": "Dota 2: CyberHero vs HULIGANI (BO3) - EPL Masters Playoffs"
        },
        {
          "kind": "Map 1 Winner",
          "outcomes": [
            "Inner Circle",
            "Spirit Academy"
          ],
          "q": "Dota 2: Inner Circle vs Spirit Academy - Game 1 Winner"
        },
        {
          "kind": "Map 2 Winner",
          "outcomes": [
            "Inner Circle",
            "Spirit Academy"
          ],
          "q": "Dota 2: Inner Circle vs Spirit Academy - Game 2 Winner"
        },
        {
          "kind": "Match Winner",
          "outcomes": [
            "Inner Circle",
            "Spirit Academy"
          ],
          "q": "Dota 2: Inner Circle vs Spirit Academy (BO3) - Asgard Championship Group A"
        }
      ],
      "ps_events": 44,
      "ps_names": [
        "cyberhero",
        "inner circle x insanity"
      ],
      "title": "dota2"
    },
    "1793342": {
      "pm_markets_sharing_a_name_token": [
        {
          "kind": "Map 1 Winner",
          "outcomes": [
            "Team Liquid",
            "DO KONCA"
          ],
          "q": "Dota 2: Team Liquid vs DO KONCA - Game 1 Winner"
        },
        {
          "kind": "Map 2 Winner",
          "outcomes": [
            "Team Liquid",
            "DO KONCA"
          ],
          "q": "Dota 2: Team Liquid vs DO KONCA - Game 2 Winner"
        },
        {
          "kind": "Match Winner",
          "outcomes": [
            "Team Liquid",
            "DO KONCA"
          ],
          "q": "Dota 2: Team Liquid vs DO KONCA (BO3) - BLAST Slam Group C"
        },
        {
          "kind": "Map 1 Winner",
          "outcomes": [
            "Froglings",
            "HULIGANI"
          ],
          "q": "Dota 2: Froglings vs HULIGANI - Game 1 Winner"
        },
        {
          "kind": "Map 2 Winner",
          "outcomes": [
            "Froglings",
            "HULIGANI"
          ],
          "q": "Dota 2: Froglings vs HULIGANI - Game 2 Winner"
        },
        {
          "kind": "Match Winner",
          "outcomes": [
            "Froglings",
            "HULIGANI"
          ],
          "q": "Dota 2: Froglings vs HULIGANI (BO3) - DreamLeague Division 2 Playoffs"
        }
      ],
      "ps_events": 20,
      "ps_names": [
        "do konca",
        "froglings"
      ],
      "title": "dota2"
    },
    "1796498": {
      "pm_markets_sharing_a_name_token": [],
      "ps_events": 9,
      "ps_names": [
        "brute",
        "nice try"
      ],
      "title": "cs2"
    },
    "1796514": {
      "pm_markets_sharing_a_name_token": [],
      "ps_events": 16,
      "ps_names": [
        "phantom",
        "wbt"
      ],
      "title": "cs2"
    },
    "1803639": {
      "pm_markets_sharing_a_name_token": [],
      "ps_events": 12,
      "ps_names": [
        "apogee esports",
        "maybe"
      ],
      "title": "cs2"
    },
    "1805736": {
      "pm_markets_sharing_a_name_token": [],
      "ps_events": 37,
      "ps_names": [
        "metizport",
        "sinners"
      ],
      "title": "cs2"
    },
    "1815178": {
      "pm_markets_sharing_a_name_token": [
        {
          "kind": "Map 1 Winner",
          "outcomes": [
            "Inner Circle",
            "Team Allied"
          ],
          "q": "Dota 2: Inner Circle vs Team Allied - Game 1 Winner"
        },
        {
          "kind": "Map 2 Winner",
          "outcomes": [
            "Inner Circle",
            "Team Allied"
          ],
          "q": "Dota 2: Inner Circle vs Team Allied - Game 2 Winner"
        },
        {
          "kind": "Match Winner",
          "outcomes": [
            "Inner Circle",
            "Team Allied"
          ],
          "q": "Dota 2: Inner Circle vs Team Allied (BO3) - European Pro League Group A"
        },
        {
          "kind": "Map 1 Winner",
          "outcomes": [
            "Spirit Academy",
            "Team Allied"
          ],
          "q": "Dota 2: Spirit Academy vs Team Allied - Game 1 Winner"
        },
        {
          "kind": "Map 2 Winner",
          "outcomes": [
            "Spirit Academy",
            "Team Allied"
          ],
          "q": "Dota 2: Spirit Academy vs Team Allied - Game 2 Winner"
        },
        {
          "kind": "Match Winner",
          "outcomes": [
            "Spirit Academy",
            "Team Allied"
          ],
          "q": "Dota 2: Spirit Academy vs Team Allied (BO3) - European Pro League Group A"
        }
      ],
      "ps_events": 0,
      "ps_names": [
        "team allied",
        "xipto esports"
      ],
      "title": "dota2"
    }
  },
  "D_timestamps": {
    "cs2_all_dead_message_to_round_score_increase_seconds": {
      "max": 201.61349368095398,
      "median": 65.37294936180115,
      "n": 23,
      "p10": 0.0,
      "p90": 167.36166787147522
    },
    "feed_clock_used_by_test": "recv_ns (our receipt, capture host clock); updated_at NOT used for lead",
    "fields_seen": {
      "recv_ns (capture row)": 4043,
      "updated_at (capture row or payload)": 4043
    },
    "note": "negative recv-updated_at means the two clocks disagree; a large positive median means the delay is before our socket (PandaScore side) or in our receive path; compare event_message vs other",
    "price_clock_used_by_test": "ms on the PM book row (same host); `sent` is the exchange send time, logged only",
    "recv_minus_updated_at_seconds": {
      "cs2|event_message": {
        "max": 3.0599825382232666,
        "median": 0.05745697021484375,
        "n": 97,
        "p10": 0.0453641414642334,
        "p90": 0.08809971809387207
      },
      "cs2|other": {
        "max": 3.1757752895355225,
        "median": 0.06351661682128906,
        "n": 3360,
        "p10": 0.05212903022766113,
        "p90": 0.09291434288024902
      },
      "dota2|event_message": {
        "max": 0.12188911437988281,
        "median": 0.05013084411621094,
        "n": 61,
        "p10": 0.04317522048950195,
        "p90": 0.08164191246032715
      },
      "dota2|other": {
        "max": 2.083623170852661,
        "median": 0.0516355037689209,
        "n": 525,
        "p10": 0.04122567176818848,
        "p90": 0.09563374519348145
      }
    }
  },
  "matched_ps_matches": 0,
  "seed": 20261116,
  "unmatched_ps_matches": 9
}
```

## run.log tail (last 40 lines)
```text
== planted tests
PASS cs2 (a) PM +10 s after the feed: n 640, median real lead 9.94 s, verdict meets bar (needs audit)
PASS cs2 (b) PM 10 s BEFORE the feed: median real lead -10.04 s, verdict no lead (needs audit)
PASS cs2 (c) PM never reacts to events (only background noise): events 640, with onset 235, verdict no lead (needs audit)
PASS dota2 (a) PM +10 s after the feed: n 640, median real lead 9.94 s, verdict meets bar (needs audit)
PASS dota2 (b) PM 10 s BEFORE the feed: median real lead -10.04 s, verdict no lead (needs audit)
PASS dota2 (c) PM never reacts to events (only background noise): events 640, with onset 235, verdict no lead (needs audit)
ALL PASS
PARTIAL FILE /tmp/tmpeg8nj431/x.jsonl.gz: error: Error -3 while decompressing data: invalid distance too far back
PARTIAL FILE /tmp/tmpeg8nj431/x.jsonl.gz: error: Error -3 while decompressing data: invalid distance too far back
PARTIAL FILE /tmp/tmpeg8nj431/x.jsonl.gz: error: Error -3 while decompressing data: invalid distance too far back
ALL PASS (rows kept before damage: 754 )
ALL PASS
ALL PASS multi/gz {'files': 3, 'rows_in': 246, 'rows_out': 233, 'dropped': 13, 'partial_files': 1}
== adapter
{"files": 48, "rows_in": 303100, "rows_out": 290115, "dropped": 12985, "partial_files": 0}
== inputs
total 876
-rw-r--r-- 1 root root 216915 2026-11-16 13:00:00.178699305 +0000 pandascore_2026111612.jsonl.gz
-rw-r--r-- 1 root root 509576 2026-11-20 21:09:19.519751657 +0000 pandascore_2026112020.jsonl.gz
-rw-r--r-- 1 root root 135718 2026-11-20 22:00:07.507745786 +0000 pandascore_2026112021.jsonl.gz
-rw-r--r-- 1 root root  13486 2026-11-20 22:02:52.882262844 +0000 pandascore_2026112022.jsonl.gz
== lead test
PARTIAL FILE /mnt/HC_Volume_107257520/pkarbs/pandascore/raw/pandascore_2026111612.jsonl.gz: error: Error -3 while decompressing data: invalid block type
PARTIAL FILE /mnt/HC_Volume_107257520/pkarbs/pandascore/raw/pandascore_2026112022.jsonl.gz: EOFError: Compressed file ended before the end-of-stream marker was reached
PARTIAL FILE /mnt/HC_Volume_107257520/pkarbs/pandascore/raw/pandascore_2026111612.jsonl.gz: error: Error -3 while decompressing data: invalid block type
PARTIAL FILE /mnt/HC_Volume_107257520/pkarbs/pandascore/raw/pandascore_2026112022.jsonl.gz: EOFError: Compressed file ended before the end-of-stream marker was reached
== audit
PARTIAL FILE /mnt/HC_Volume_107257520/pkarbs/pandascore/raw/pandascore_2026111612.jsonl.gz: error: Error -3 while decompressing data: invalid block type
PARTIAL FILE /mnt/HC_Volume_107257520/pkarbs/pandascore/raw/pandascore_2026112022.jsonl.gz: EOFError: Compressed file ended before the end-of-stream marker was reached
```

## PARTIAL FILE lines
```text
PARTIAL FILE /tmp/tmpeg8nj431/x.jsonl.gz: error: Error -3 while decompressing data: invalid distance too far back
PARTIAL FILE /tmp/tmpeg8nj431/x.jsonl.gz: error: Error -3 while decompressing data: invalid distance too far back
PARTIAL FILE /tmp/tmpeg8nj431/x.jsonl.gz: error: Error -3 while decompressing data: invalid distance too far back
PARTIAL FILE /mnt/HC_Volume_107257520/pkarbs/pandascore/raw/pandascore_2026111612.jsonl.gz: error: Error -3 while decompressing data: invalid block type
PARTIAL FILE /mnt/HC_Volume_107257520/pkarbs/pandascore/raw/pandascore_2026112022.jsonl.gz: EOFError: Compressed file ended before the end-of-stream marker was reached
PARTIAL FILE /mnt/HC_Volume_107257520/pkarbs/pandascore/raw/pandascore_2026111612.jsonl.gz: error: Error -3 while decompressing data: invalid block type
PARTIAL FILE /mnt/HC_Volume_107257520/pkarbs/pandascore/raw/pandascore_2026112022.jsonl.gz: EOFError: Compressed file ended before the end-of-stream marker was reached
PARTIAL FILE /mnt/HC_Volume_107257520/pkarbs/pandascore/raw/pandascore_2026111612.jsonl.gz: error: Error -3 while decompressing data: invalid block type
PARTIAL FILE /mnt/HC_Volume_107257520/pkarbs/pandascore/raw/pandascore_2026112022.jsonl.gz: EOFError: Compressed file ended before the end-of-stream marker was reached
```

## Result
- The run completed successfully, but the lead result is not evaluable: both Dota cells have 0 events and 0 matches; 9 PandaScore matches were seen and all 9 were unmatched to Polymarket. `strata_computed` is false.
- The runner reported partial/corrupt gzip input for the 2026-11-16 PandaScore file and an incomplete gzip stream for the actively written 2026-11-20 22:00 file; no input was modified.
- Audit reconciliation counted 38 kill, 15 tower, 3 Roshan, and 8 barracks increases across the matched feed records. Dota lead verdict remains unknown (n<30).
- No non-zero process exit. The task asks to record these findings, not to repair inputs or judge the feed.
