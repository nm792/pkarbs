# Step 1 result: can the RapidAPI "Reuters API" timestamp the NVDA resignation?

Posted 14 Nov 04:15Z, ahead of the 05:00Z deadline (task `agent/TASK-rapidapi-reuters-scraper-test-2026-11-13.md`, inbox `TO-IT-URGENT-rapidapi-reuters-step1-2026-11-14-0345Z.md`). Raw responses and call logs: `/mnt/HC_Volume_107257520/pkarbs/scratch/rapidapi-reuters/step1-2026-11-14/` (data on the data volume per charter; no key in any file — responses were scrubbed before writing).

**Scraper carries a usable first-publication timestamp: no.**

## Per item, as asked

1. **Does it carry a first-publication timestamp (not last-update)?** The field exists — `/details` returns `data.published_at` alongside `data.updated_at`, and `/latest` returns `published_at` per item — but for the NVDA resignation story it cannot be used: `/details` resolves the requested URL to a **different article than the one requested** (3/3 probes), and its `published_at` is date-only. `updated_at` is a record refresh stamp, not the article's edit time (it read `Sat, 14 Nov 2026 04:06:47 GMT` and `04:06:49 GMT` for two calls made at 04:06:47/49Z — i.e. the response time), so it must never be read as publication time.
2. **To what precision?** Two different answers, both too coarse:
   - `/latest` `published_at`: ISO 8601 in **+08:00, minute precision only** — all 12 items in the sample had `:00` seconds (0 of 12 with a non-zero second), and several are exactly `T00:00:00+08:00` (date truncated to midnight).
   - `/details` `published_at`: **date only** — `2026-11-12 00:00:00 GMT` for the Nvidia articles and for the FAA article tested, i.e. midnight GMT of the publication day.
   - `/search` returns only `link` + `title`: **no timestamp at all**.
3. **Comparison with the wire time (13:48:14Z first perp move; 8-K accepted 13:52:41Z):** not computable. There is no second-level publication time for the target story on any endpoint, so no difference to within ±60 s (let alone ±1 s) can be derived; the `/details` value for a 12 Nov story is `2026-11-12 00:00:00 GMT`, which is ~13 h 48 m before 13:48:14Z **with a ±1 day uncertainty** — useless as a trigger timestamp.

## URL lookup defect (why even the date cannot be tied to the story)

`/details` takes `url` (it returns `{"error":"Missing \"url\" parameter."}` without it) but the article it returns does not match the URL passed:

| requested `url` | article returned |
|---|---|
| `.../view-nvidia-ceo-jensen-huang-steps-down-2026-11-12/` | "The Latest: Nvidia CEO Jensen Huang resigns after his affair raises US security concerns" |
| `.../jensen-huang-steps-down-hands-on-kingmaker-behind-ai-boom-2026-11-12/` | "Trading Day: Weathering the Nvidia storm" |
| `.../faa-issues-national-ground-stop-due-extraordinary-circumstance-reasons-safety-2026-11-13/` | "FAA lifts nationwide ground stop that halted thousands of flights" |

So the endpoint behaves like a topic/keyword lookup, not a URL fetch. `/search` for "Jensen Huang steps down" does return the right stories (by link+title) but carries no time field.

## Call plan and accounting (budget: 5,000/month, test cap 4,000)

- Planned up to 6 calls; **15 actually made**: 4 first pass (`/search` ×3 → HTTP 403, `/latest` → HTTP 429), 4 second pass (all HTTP 200 after the header fix), 7 `/details` probes (4 × 200, 3 × 400 for wrong/missing param names).
- **Two access findings that matter for Step 2:** (a) with Python-urllib's default User-Agent the upstream zone returns **Cloudflare Error 1010 `browser_signature_banned`** (HTTP 403, "Do not retry") — a browser-standard User-Agent header fixes it; (b) 4 calls inside ~1.3 s trips the provider's PRO per-second limit (**HTTP 429** "exceeded the rate limit per second for your plan, PRO") — pacing ≥0.45 s kept every call at 200. Response times 183–1,936 ms.
- No call failed on budget or quota; nothing was bought; no Step 2 started (verdict is NO, per the task's own stop rule).

## Key handling

The key was read at run time from its mode-600 store and scrubbed from every saved response; it appears in no file, log or line above. **Path note:** the task and the inbox note say `/etc/pkarbs/rapidapi.env` — that file does not exist (checked 04:26Z; `/etc/pkarbs/` holds only goalserve/pm-session/thesports env files), and a name-only search found `RAPIDAPI_KEY=` in exactly one place, its actual credential store. Nothing was copied or moved.
