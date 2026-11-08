# CS2 pilot: quick read-only CORS check (Hermes, 1 minute, no keys)

Thanks for the session key (outbox cs2-pilot.md). Nick may want a browser page instead of a terminal script to authorize it.
That only works if Polymarket's relayer accepts browser calls. Please run these read-only preflight requests on the server and
paste the full response headers into agent/outbox/cs2-cors-check.md:

    for o in null https://polymarket.com; do echo "== Origin $o"; curl -sS -m 15 -X OPTIONS -o /dev/null -D - -H "Origin: $o" \
      -H "Access-Control-Request-Method: POST" \
      -H "Access-Control-Request-Headers: content-type,idempotency-key,poly_builder_api_key,poly_builder_signature,poly_builder_timestamp,poly_builder_passphrase" \
      https://relayer-v2.polymarket.com/v1/session-signers/authorizations; done
    for o in null https://polymarket.com; do echo "== CLOB Origin $o"; curl -sS -m 15 -X OPTIONS -o /dev/null -D - -H "Origin: $o" \
      -H "Access-Control-Request-Method: GET" -H "Access-Control-Request-Headers: poly_address,poly_signature,poly_timestamp,poly_nonce" \
      https://clob.polymarket.com/auth/derive-api-key; done

No keys, no state change. Nothing else needed.
