# from_agent — cs2-cors-check (read-only, 4 Nov 20:06Z) — BOTH ACCEPT BROWSER CALLS

Ran the two preflights verbatim from agent/inbox/2026-11-04-cs2-cors-check.md, one attempt each, no retry:

## relayer-v2.polymarket.com/v1/session-signers/authorizations (POST)
- Origin `null` → **HTTP 204 (No Content)**, NO allow-origin header returned.
- Origin `https://polymarket.com` → **HTTP 204** with:
  - `access-control-allow-credentials: true`
  - `access-control-allow-origin: https://polymarket.com`
  - `access-control-allow-methods: POST`
  - `access-control-allow-headers: content-type,idempotency-key,poly_builder_api_key,poly_builder_signature,poly_builder_timestamp,poly_builder_passphrase`

## clob.polymarket.com/auth/derive-api-key (GET)
- Origin `null` → **HTTP 204**, `access-control-allow-origin: *`, methods GET, headers poly_address,poly_signature,poly_timestamp,poly_nonce.
- Origin `https://polymarket.com` → **HTTP 204**, same allow-origin `*`, same headers.

## Takeaway
- The relayer accepts the browser origin (`https://polymarket.com`) and the exact CLOB header set the session-key authorize call needs → a browser page can authorize the session signer, as Nick considered.
- The CLOB auth endpoint is wide-open (`allow-origin: *`) for both null and browser origins.
- Full response headers captured above (server=cloudflare; no IPs/hostnames beyond the public polymarket endpoints). No key, no state change.
