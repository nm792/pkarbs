"""Shared EV rule for Polymarket binary outcome tokens.

All prices are per share of a token that pays $1 if the outcome happens.
fair q   = our model probability of the outcome.
Fees (Polymarket docs, trading/fees, Sports row): taker fee per share
      = rate * p * (1 - p), rate = 0.05 for Sports (esports are Sports).
Makers pay no fee. Maker rebate = 15% of taker fees in the market, paid
pro rata to makers by filled volume. We approximate our rebate per filled
share as REBATE_SHARE * rate * p * (1 - p). That is an ESTIMATE: the real
payout depends on our share of maker volume that day.
"""
import math
from dataclasses import dataclass, field

SPORTS_FEE_RATE = 0.05
REBATE_SHARE = 0.15


def taker_fee(p, rate=SPORTS_FEE_RATE):
    return rate * p * (1.0 - p)


def maker_rebate_est(p, rate=SPORTS_FEE_RATE, share=REBATE_SHARE):
    return share * rate * p * (1.0 - p)


def ev_take_buy(q, ask, rate=SPORTS_FEE_RATE):
    """EV per share of buying the token at the ask as a taker."""
    return q - ask - taker_fee(ask, rate)


def ev_take_sell(q, bid, rate=SPORTS_FEE_RATE):
    """EV per share of selling the token at the bid as a taker
    (same as buying the other side at 1 - bid)."""
    return bid - q - taker_fee(bid, rate)


def ev_make_buy(q, price, rate=SPORTS_FEE_RATE, adverse=0.0):
    """EV per share of a resting bid that gets filled at `price`.
    `adverse` = expected adverse-selection loss per share when filled
    (LoL top makers' 60 s markout was -2c to -16c per $, so it is large)."""
    return q - price + maker_rebate_est(price, rate) - adverse


def ev_make_sell(q, price, rate=SPORTS_FEE_RATE, adverse=0.0):
    return price - q + maker_rebate_est(price, rate) - adverse


@dataclass
class Limits:
    """Risk caps. Defaults assume a $10k bankroll (an assumption, change it)."""
    bankroll: float = 10_000.0
    kelly_frac: float = 0.10          # tenth-Kelly: model error is large
    max_order_frac: float = 0.01      # one order <= 1% of bankroll
    max_market_frac: float = 0.02     # one outcome token <= 2%
    max_match_frac: float = 0.04      # one match, all its markets <= 4%
    max_open_frac: float = 0.15       # everything open <= 15% (worst case loss)
    daily_stop_frac: float = 0.03     # stop the day at -3% realised+marked
    max_depth_take: float = 0.5       # never take more than 50% of shown size
    min_price: float = 0.04           # no trades in the tails, fees+model error
    max_price: float = 0.96
    max_feed_age_s: float = 5.0       # stale feed -> no new trades


@dataclass
class StageCaps:
    """Hard $ caps for live trading, applied ON TOP of Limits (the smaller wins).
    Nick 2 Nov: live starts at tiny amounts. Moving up a stage needs a
    human review of paper + live results; code never promotes itself."""
    name: str
    max_order_usd: float
    max_market_usd: float
    max_match_usd: float
    max_open_usd: float
    daily_stop_usd: float


STAGES = {
    'paper':  None,                                              # Limits only, no real money
    'live_1': StageCaps('live_1', 5, 10, 20, 50, 20),            # first live week
    'live_2': StageCaps('live_2', 25, 50, 100, 250, 75),         # after review of live_1
    'live_3': StageCaps('live_3', 100, 200, 400, 1500, 300),     # = full $10k Limits
}


def apply_stage(lim: 'Limits', stage: str) -> 'Limits':
    """Return Limits shrunk to the stage's $ caps (fractions of bankroll)."""
    c = STAGES[stage]
    if c is None:
        return lim
    B = lim.bankroll
    return Limits(bankroll=B, kelly_frac=lim.kelly_frac,
                  max_order_frac=min(lim.max_order_frac, c.max_order_usd / B),
                  max_market_frac=min(lim.max_market_frac, c.max_market_usd / B),
                  max_match_frac=min(lim.max_match_frac, c.max_match_usd / B),
                  max_open_frac=min(lim.max_open_frac, c.max_open_usd / B),
                  daily_stop_frac=min(lim.daily_stop_frac, c.daily_stop_usd / B),
                  max_depth_take=lim.max_depth_take, min_price=lim.min_price, max_price=lim.max_price,
                  max_feed_age_s=lim.max_feed_age_s)


@dataclass
class SportRule:
    name: str
    min_edge_taker: float             # $ per share after fees
    min_edge_maker: float
    model_sd: float                   # rough 1-sd error of q (prob units)
    z: float = 1.0                    # also need edge >= z * model_sd
    maker_adverse: float = 0.03       # assumed adverse selection per filled share


@dataclass
class Decision:
    action: str                       # 'buy', 'sell' or 'none'
    price: float = 0.0
    shares: float = 0.0
    edge: float = 0.0
    reason: str = ''
    detail: dict = field(default_factory=dict)


def kelly_shares(q, cost, bankroll, frac):
    """Fractional Kelly for buying a $1 binary at all-in cost `cost`."""
    if cost <= 0 or cost >= 1 or q <= cost:
        return 0.0
    f = (q - cost) / (1.0 - cost)
    return frac * f * bankroll / cost


def decide_taker(q, best_bid, bid_size, best_ask, ask_size, rule: SportRule,
                 lim: Limits = Limits(), feed_age_s=0.0, market_pos=0.0,
                 match_pos=0.0, open_pos=0.0, day_pnl=0.0):
    """Taker decision for one outcome token.
    positions are $ at cost (positive = long this token)."""
    if day_pnl <= -lim.daily_stop_frac * lim.bankroll:
        return Decision('none', reason='daily stop hit')
    if feed_age_s > lim.max_feed_age_s:
        return Decision('none', reason=f'feed stale {feed_age_s:.1f}s')
    need = max(rule.min_edge_taker, rule.z * rule.model_sd)
    cands = []
    if best_ask and lim.min_price <= best_ask <= lim.max_price:
        e = ev_take_buy(q, best_ask)
        cands.append(('buy', best_ask, ask_size, e, best_ask + taker_fee(best_ask), q))
    if best_bid and lim.min_price <= best_bid <= lim.max_price:
        e = ev_take_sell(q, best_bid)
        # selling the token == buying the other side at 1-bid
        cands.append(('sell', best_bid, bid_size, e, 1 - best_bid + taker_fee(best_bid), 1 - q))
    if not cands:
        return Decision('none', reason='no price in range')
    side, px, size, e, cost, qq = max(cands, key=lambda c: c[3])
    if e < need:
        return Decision('none', edge=e, reason=f'edge {e:.3f} < need {need:.3f}')
    sh = kelly_shares(qq, cost, lim.bankroll, lim.kelly_frac)
    caps = {
        'kelly': sh,
        'order': lim.max_order_frac * lim.bankroll / cost,
        'depth': lim.max_depth_take * (size or 0.0),
        'market': max(0.0, lim.max_market_frac * lim.bankroll - abs(market_pos)) / cost,
        'match': max(0.0, lim.max_match_frac * lim.bankroll - abs(match_pos)) / cost,
        'open': max(0.0, lim.max_open_frac * lim.bankroll - abs(open_pos)) / cost,
    }
    binding = min(caps, key=caps.get)
    sh = caps[binding]
    if sh < 5:   # Polymarket minimum order is 5 shares on most books
        return Decision('none', edge=e, reason=f'size {sh:.1f} too small ({binding} cap)')
    return Decision(side, px, math.floor(sh * 10) / 10, e, reason=f'edge {e:.3f} >= {need:.3f}; size cap {binding}',
                    detail=caps)


def maker_quotes(q, rule: SportRule, tick=0.01):
    """Bid and ask we would rest around fair q (None = do not quote).
    Each side must clear min_edge_maker after the assumed adverse selection,
    counting the estimated rebate. The caller cancels on every game event."""
    need = max(rule.min_edge_maker, rule.z * rule.model_sd)
    bid = math.floor((q - need) / tick) * tick
    while bid >= 0.04 and ev_make_buy(q, bid, adverse=rule.maker_adverse) < need:
        bid -= tick
    ask = math.ceil((q + need) / tick) * tick
    while ask <= 0.96 and ev_make_sell(q, ask, adverse=rule.maker_adverse) < need:
        ask += tick
    return (round(bid, 2) if bid >= 0.04 else None, round(ask, 2) if ask <= 0.96 else None)
