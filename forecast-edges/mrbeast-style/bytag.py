import json,urllib.request,time,sys,collections
def get(u):
    for a in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'x'}),timeout=40))
        except Exception as e: time.sleep(1+a)
TAGS={'mrbeast':145,'mrbeast2':101098,'mrbeast3':101099,'beast':101097+4,'views':618,'viewer':101791,'viewers':102222,'subscribers':147,'youtube':146,'spotify':102851,'appstore':970,'creator':102005,'creators':101110,'influencers':1440,'infl2':277,'twitch':100360,'streamer':100636,'ishowspeed':100359,'kai':100352,'tiktok':530,'charts':724,'billboard':103077,'bhot':723,'netflix':100407,'topnetflix':102952,'googlesearch':102823,'google':663,'steam':101553,'podcast':100749,'livestream':101460,'streaming':103004,'rankings':967,'top10':103259,'socialmedia':127,'applemusic':1347,'truth':100358,'speedkai':100355,'speed':100354}
ev={}
for name,t in TAGS.items():
    n0=len(ev)
    for closed in ('true','false'):
        off=0
        while off<6000:
            j=get(f'https://gamma-api.polymarket.com/events?tag_id={t}&closed={closed}&limit=100&offset={off}')
            if not j: break
            for e in j:
                ev[e['id']]=dict(id=e['id'],title=e['title'],slug=e.get('slug'),vol=e.get('volume'),end=e.get('endDate'),start=e.get('startDate'),closed=e.get('closed'),nm=len(e.get('markets') or []),tag=name)
            if len(j)<100: break
            off+=100
    print(name,len(ev)-n0,len(ev),flush=True)
json.dump(ev,open('tagev.json','w'))
