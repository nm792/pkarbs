import os, sys, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pit_store as P

def row(cond, ts=1): return dict(timestamp=ts, side="BUY", token_id="t", price=0.5, size=1, outcome_index=0, condition_id=cond)

def fake(pages):
    it = iter(pages)
    return lambda url, *a, **k: next(it)

def test_pull_trades_accepts_rows_for_the_requested_condition(monkeypatch):
    monkeypatch.setattr(P, "http_json", fake([dict(data=[row("0xAB")], pagination=dict(has_more=False))]))
    out, trunc = P.pull_trades("0xab")
    assert len(out) == 1 and not trunc                      # case-insensitive match

def test_planted_wrong_param_other_market_rows_must_fail(monkeypatch):
    """the real failure: a misspelled param (markets=) is ignored and OTHER markets' trades come back."""
    monkeypatch.setattr(P, "http_json", fake([dict(data=[row("0xAB"), row("0xCD")], pagination=dict(has_more=False))]))
    with pytest.raises(RuntimeError, match="other conditions"):
        P.pull_trades("0xab")

def test_check_condition_unit():
    P.check_condition([row("0xab")], "0xAB")
    with pytest.raises(RuntimeError): P.check_condition([row("0xzz")], "0xab")
    with pytest.raises(RuntimeError): P.check_condition([dict(price=1)], "0xab")      # row without condition_id is also refused
