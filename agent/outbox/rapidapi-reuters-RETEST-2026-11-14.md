APPROVALS NEEDED: none
RESULT
- Verdict: **Scraper carries a usable first-publication timestamp to the second: no.**
- 24 API requests were logged (within the 300-call cap); 10 direct article-page checks returned HTTP 401. No retry or access workaround was attempted.
- Huang test: 10 search results were checked through `/details`; 0/10 returned the searched title. `published_at` was date-only for four and equal to the request-time stamp for six; none establishes first publication.
- The `/latest` sample below has minute-rounded seconds (`:00`) throughout. `/details` returned date-only values for all 10; only two returned titles matched the `/latest` title.
| /latest article (short) | /latest published_at | /details published_at | title match |
|---|---|---|---|
| Old air traffic control equipment regularly disrupts US flights | 2026-11-14T00:00:00+08:00 | 2026-11-14 00:00:00 GMT | no |
| Canada, US make progress on trade deal, Carney says | 2026-11-14T00:00:00+08:00 | 2026-11-14 00:00:00 GMT | no |
| Riots in France: How anti-government protests spiraled out of control | 2026-11-14T00:00:00+08:00 | 2026-11-14 00:00:00 GMT | no |
| South Korea should not fear China's rise, foreign minister says | 2026-11-14T00:00:00+08:00 | 2026-11-14 00:00:00 GMT | no |
| US to resume flights after air traffic network failure sparks chaos | 2026-11-13T21:38:00+08:00 | 2026-11-13 00:00:00 GMT | no |
| US flight shutdown exposes deepening air traffic network crisis | 2026-11-14T00:00:00+08:00 | 2026-11-14 00:00:00 GMT | yes |
| Rubio assails international court in speech to conservative legal group | 2026-11-14T00:00:00+08:00 | 2026-11-14 00:00:00 GMT | yes |
| US National Weather Service says its radars operating normally | 2026-11-13T22:13:00+08:00 | 2026-11-13 00:00:00 GMT | no |
| Hours-long halt to US flights leaves travelers frustrated, anxious | 2026-11-14T00:00:00+08:00 | 2026-11-14 00:00:00 GMT | no |
| Wall St Week Ahead: Nvidia results, Anthropic IPO pose tests for tumultuous AI trade | 2026-11-13T11:11:00+08:00 | 2026-11-13 00:00:00 GMT | no |
- Reuters page metadata: all 10 direct checks returned HTTP 401; no publication metadata was available. The note’s stop-on-block rule was followed.
- `/details` documentation example uses a full article URL in the `url` query parameter; path-only was tested and returned 400. Public docs exposed `/category` and `/details`; `/latest` and `/search` parameter documentation was not exposed by the fetched listing. Observed `/search` used `q`.
DATA
- Raw calls and summaries: `pkarbs/scratch/rapidapi-reuters/retest-2026-11-14/` on the data disk (not committed).
OPEN / NOT VERIFIED
- First-publication time to the second remains unavailable; page metadata was blocked with HTTP 401.
- Call-start timestamps were not retained, so the required >=0.5 s pacing cannot be independently audited from the saved call log.
Count: notes run 1, outstanding 0, PENDING open 0
