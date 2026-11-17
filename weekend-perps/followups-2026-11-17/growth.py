"""Writes growth.json ({dex: {asset: growthMode}}) from the live Hyperliquid meta call. Run next to hist.py/cand.py: python3 growth.py
Without this file every fee falls back to the non-growth 9 bp (perplib.fee_info)."""
import json, requests
HL = "https://api.hyperliquid.xyz/info"; out = {}
for d in ("xyz", "flx", "km"):
    out[d] = {u["name"]: u.get("growthMode") for u in requests.post(HL, json={"type": "meta", "dex": d}, timeout=30).json()["universe"]}
json.dump(out, open("growth.json", "w")); print({d: len(v) for d, v in out.items()})
