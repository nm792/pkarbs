import sys,json,urllib.request,time
def get(u,retry=4):
    for i in range(retry):
        try:
            r=urllib.request.Request(u,headers={"User-Agent":"curl/8.0"})
            return json.load(urllib.request.urlopen(r,timeout=30))
        except Exception as e:
            err=e; time.sleep(1+i)
    raise err
if __name__=="__main__":
    u=sys.argv[1].replace("^^","?").replace("~~","&")
    d=get(u)
    s=json.dumps(d)
    if len(sys.argv)>2: open(sys.argv[2],"w").write(s)
    print(s[:int(sys.argv[3]) if len(sys.argv)>3 else 1500])
