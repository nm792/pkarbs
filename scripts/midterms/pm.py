import json,re,sys
def load(f):
    d=json.load(open(f)); out=[]
    for r in d['results']:
        t=r['text']; t=re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', t)
        try: out.append(json.loads(t))
        except Exception as e: print('ERR',r['url'],e)
    return out
def show(e, rules=True):
    print('=== ',e['slug'],'negRisk',e.get('negRisk'),'aug',e.get('enableNegRisk'),e.get('negRiskAugmented'),'end',e.get('endDate'))
    if rules: print('DESC:',(e.get('description') or '')[:1500])
    sa=0;sb=0
    for m in e.get('markets',[]):
        if m.get('closed'): continue
        a=m.get('bestAsk'); b=m.get('bestBid')
        act=m.get('active') and m.get('acceptingOrders')
        print(f"  {m.get('groupItemTitle') or m.get('question')!s:45.45} bid {b} ask {a} last {m.get('lastTradePrice')} liq {round(float(m.get('liquidityNum') or 0))} acc {m.get('acceptingOrders')} fee {m.get('feeSchedule') or m.get('feesEnabled')} plc {m.get('negRiskOther')}")
        if act and a is not None: sa+=float(a); sb+=float(b or 0)
    print('  SUM ask',round(sa,4),'SUM bid',round(sb,4))
if __name__=='__main__':
    for e in load(sys.argv[1]): show(e, rules=len(sys.argv)<3)
