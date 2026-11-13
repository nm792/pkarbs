"""Convert v2 activity + v2 taker trades (snake_case) to the v1 shapes decomp.py reads.
Usage: v2_to_v1.py activity.jsonl.gz taker.jsonl.gz out_act.json.gz out_trades_dir"""
import gzip,json,sys,os
a=[json.loads(l) for l in gzip.open(sys.argv[1],'rt')]; t=[json.loads(l) for l in gzip.open(sys.argv[2],'rt')]
def conv(x): return dict(type=x.get('type','TRADE'),transactionHash=x['transaction_hash'],asset=x['token_id'],size=x['size'],price=x['price'],timestamp=x['timestamp'],eventSlug=x['event_slug'],slug=x['slug'],conditionId=x['condition_id'],usdcSize=x.get('usdc_size'))
json.dump([conv(x) for x in a if x['type']=='TRADE'],gzip.open(sys.argv[3],'wt'))
os.makedirs(sys.argv[4],exist_ok=True); json.dump({'rows':[conv(x) for x in t]},open(sys.argv[4]+'/true_all.json','w'))
