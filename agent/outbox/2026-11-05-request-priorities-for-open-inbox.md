# Question to the PK arbs owner — priority order for the open inbox queue

The agent inbox holds ~40 unanswered tasks across: cs2 logger (ws-logger, count-mismatch, restart-proof, cors-check, pilot-dryrun, session-key + verify, freshness/0805Z), cricket (npl-live, capture approved, commit-windows A/B), dota live-capture, crossbet reachability, storage (offload-verify-all, stale-copies, copies-and-gen-lyon, offload-ruling), and misc (fix-poll-and-status, rugbyrama-poll, nick-approvals-code-gate, hltv-cs2-rounds), plus the TASK-gates-* series (02Z-toprepair, all-hours, one-hour, rerun) and rescan/coverage keepers.

Which items should the agent work first, and in what order? I will execute the read-only ones immediately and raise every gated item as a button before touching code/collectors. If the owner would rather I just proceed oldest-first through the read-only subset and raise the rest, say so.
