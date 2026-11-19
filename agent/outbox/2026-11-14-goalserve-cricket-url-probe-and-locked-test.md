# Goalserve cricket URL probe — 16 Nov 2026, 12:05Z

## Measured results

| Probe | Result |
|---|---|
| `inplay-cricket.gz` on the existing in-play host | HTTP 404 |
| Authenticated `/getfeed/<key>/cricket/livescore?json=1` on the existing in-play host | HTTP 404; 0 response bytes |
| Authenticated `/getfeed/<key>/cricket/home?json=1` on the existing in-play host | HTTP 404; 0 response bytes |
| `cricket/livescore` on the previously tested livescore host | HTTP 400; empty body |
| `cricket/livescore` on the live host | HTTP 404; empty body |
| Token endpoint | HTTP 200; token remained in process memory only |
| WebSocket `/ws/cricket` and `/ws/cricket-live` | Both produced a connection-error event, zero messages. Node's built-in WebSocket does not expose the handshake status/close code here, so those are unmeasured. |

No endpoint returned a live match; no 10-minute capture was started. No credential value was printed or written.

## Account documentation check

The public cricket API description lists live scores and ball-by-ball data, but its sample pages direct customers to support for JSON samples and feed structure. Existing project notes contained no account feed-index URL. The public `/en/login` and `/login` paths returned the public site shell with no login form; I did not submit credentials, and did not reach an authenticated account feed index. The exact authenticated account path is unavailable in this run.

## Conclusion

No working live-cricket endpoint/channel was found. Ask Goalserve support for the exact live ball-by-ball endpoint and auth form for this account, its update rate, and confirmation live cricket is included in the current plan. No email was sent. The locked latency test remains unrun because there is neither a working feed nor a live match; no latency verdict is claimed.
