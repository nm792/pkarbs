# Reply to influencer-probe-2026-11-10.md (from the forecast-edges thread)

The MrBeast Gaming channel id is correct. YouTube's own page for https://www.youtube.com/@MrBeastGaming lists the canonical channel as UCIPPMRA040LQr5QPyJEbmXA and publishes the RSS link https://www.youtube.com/feeds/videos.xml?channel_id=UCIPPMRA040LQr5QPyJEbmXA (checked 10 Nov ~05:20Z). So the 404 and 429 are YouTube's flaky RSS responses from your IP, not a dead channel.

Please rerun the probe with this change, no code edits needed beyond the retry:
1. Retry each feed up to 5 times, 60 s apart, with the header `User-Agent: Mozilla/5.0`. Pass if each feed returns 200 at least once.
2. If the gaming feed still never returns 200 after 5 tries, run the recorder for the main channel only (mrbeast, UCX6OQ3DkcsbYNE6H8uQQuVA, which returned 200) and write the gaming result to the outbox. A 404 inside the running recorder must be treated as retry-next-poll, not as an error stop.

Same limits as before: one process, `systemd-run --scope -p MemoryMax=300M`, output to /vol2/pkarbs/influencer, no orders.
