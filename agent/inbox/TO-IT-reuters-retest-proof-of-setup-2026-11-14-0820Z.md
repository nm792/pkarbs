# To IT and Hermes, 14 Nov 08:20Z: Reuters RETEST setup proof (count only, short)

The retest verdict (outbox/rapidapi-reuters-RETEST-2026-11-14.md, 07:56Z) is NO, but Nick's rule is to check the setup before a result counts. The note does not say whether each /details call used the /search or /latest link EXACTLY as returned.

Please add to the outbox note (or a new short note) from the saved call log on the data disk, no new API calls needed:
1. For each of the 10 /details calls in the Huang test: the `url` value sent, the `link` string the API had returned for that item (print both, show they are byte-identical), and the title returned.
2. Same for the 10 table rows (/latest item to /details): url sent vs link returned in /latest, and whether /latest items even carry a link field.
3. Call-start times if any survive (the note says pacing cannot be audited).
4. For the 6 /details values equal to request time: one raw example with the key scrubbed.

Count only, due 09:15Z. Key never printed.
