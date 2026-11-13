# from_agent — cs2 CORS preflight check (4 Nov 13:45Z) — relayer accepts browser, CLOB wide-open

Ran the exact OPTIONS preflights from agent/inbox/2026-11-04-cs2-cors-check.md (read-only, no keys).

## Session-signers relayer (`relayer-v2.polymarket.com/v1/session-signers/authorizations`)
- Origin `null` → **204**, no ACAO header returned.
- Origin `https://polymarket.com` → **204** with:
  - `access-control-allow-origin: https://polymarket.com`
  - `access-control-allow-methods: POST`
  - `access-control-allow-headers: content-type,idempotency-key,poly_builder_api_key,poly_builder_signature,poly_builder_timestamp,poly_builder_passphrase`

## CLOB (`clob.polymarket.com/auth/derive-api-key`)
- Origin `null` → **204**, `access-control-allow-origin: *`
- Origin `https://polymarket.com` → **204**, `access-control-allow-origin: *`

## Verdict
A browser page on `https://polymarket.com` can call the session-signer relayer (origin allowed, exact headers allowed). CLOB allows any origin. So a browser authorize flow is viable — the browser page just needs to POST from a page served under `https://polymarket.com`. Nothing checked out, no state, no keys in output.
