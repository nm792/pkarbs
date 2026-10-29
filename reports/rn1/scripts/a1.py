import json,datetime as dt
p=json.load(open("pnl.json"))["data"]["points"]
print(len(p)); print(p[-1])
keys=["realized_market_pnl","realized_lp_pnl","realized_combo_pnl","unrealized_pnl","fees_refunded","maker_rebate","taker_rebate","reward_income","yield_income","referral_income","sponsored_income","fees","fees_paid","economic_pnl","trade_pnl","volume","volume_usdc","trade_count","deposits","withdrawals"]
# test cumulative?
for i in [1,2,3,len(p)//2,-2]:
    print(dt.datetime.utcfromtimestamp(p[i]["timestamp"]).date(), {k:p[i][k] for k in ["economic_pnl","volume","trade_count","maker_rebate","fees_paid"]})
