from g import get
W="0x2005d16a84ceefa912d4e380cd32e7ff827875ea"
for off in [500,1000,2000,3000,3500,5000]:
    try: print(off,len(get(f"https://data-api.polymarket.com/activity?user={W}&limit=500&offset={off}",retry=1)))
    except Exception as e: print(off,e)
