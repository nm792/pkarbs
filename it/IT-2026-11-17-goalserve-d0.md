# IT to PK arbs, 17 Nov 2026 09:15Z: Goalserve D0 routed; deviation noted

1. **Goal:** measure Goalserve odds against Polymarket books to find tradable feed-delay arbs.
2. **Where it stands:** chunk B done (P15a, pkarbs 6822261e); chunk A install (OPEN P15b) open since 08:45Z, no agent commit on it yet; chunk C (P15c) waits after it.
3. **The one item that matters most:** P15b, the store-all capture install, since C, D0 and D all depend on its data.

- **D0 routed** as OPEN P15d0 (waiting: after P15c; dialogue 51a5775d): the note's five read-only commands, outputs unedited, plus the Prime/gateway clock line, to agent/status/goalserve-pm-dirs-and-clock-2026-11-17.md.
- **Deviation answer (Nick 08:33:16Z) noted;** it is no longer a NEEDS NICK item.
- Chunk D is routed only after D0 lands and you re-post D (P15d) with the exact `--pm` dirs and clock note.
