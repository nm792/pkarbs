import os, tempfile, pyarrow as pa, pyarrow.parquet as pq, urllib.error, io, pmxt_gas_filter as m
def mk(path, ids):
    pq.write_table(pa.table({"asset_id": ids, "best_ask": [0.5]*len(ids)}), path)
def test_filter_keeps_only_gas():
    t = pa.table({"asset_id": ["a", "b", "c", "a"], "x": [1, 2, 3, 4]})
    sub, col = m.filter_table(t, {"a": 1}); assert col == "asset_id" and sub.num_rows == 2
    sub, _ = m.filter_table(t, {"zzz": 1}); assert sub.num_rows == 0   # can fail: a wrong token matches nothing
def test_process_hour_ok_missing_and_guard():
    d = tempfile.mkdtemp(); src = os.path.join(d, "h.parquet"); mk(src, ["a", "b", "a"])
    out = os.path.join(d, "o"); os.makedirs(out)
    r = m.process_hour("file://" + src, out, {"a": 1}, 0); assert r == ("OK", 3, 2), r
    assert not any(f.endswith(".part") for f in os.listdir(out))
    def nf(u): raise urllib.error.HTTPError(u, 404, "x", {}, io.BytesIO())
    assert m.process_hour("http://x/y.parquet", out, {"a": 1}, 0, opener=nf)[0] == "MISSING"
    try: m.process_hour("file://" + src, out, {"a": 1}, 10**9); assert False
    except SystemExit as e: assert "STOP" in str(e)
def test_slug_and_tokens():
    import datetime as dt
    assert m.slug_for(dt.date(2026, 11, 5)) == "us-gas-price-on-november-5-2026"
    fake = lambda u: [{"markets": [{"clobTokenIds": '["y1","n1"]', "question": "q"}]}]
    assert set(m.resolve_tokens([dt.date(2026, 11, 5)], fake)) == {"y1", "n1"}
if __name__ == "__main__":
    test_filter_keeps_only_gas(); test_process_hour_ok_missing_and_guard(); test_slug_and_tokens(); print("3 of 3 PASS")
