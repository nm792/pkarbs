import re,json,glob
T={'AI 50+':r"\bAI(?:'s|s)?\b",'DRAM / NAND 3+':r"\b(?:DRAM|NAND)s?\b",'Vera Rubin':r"\bVera Rubin\b",'Inference':r"\binferences?\b",'Shortage':r"\bshortages?\b",'Blackwell':r"\bBlackwell(?:'s)?\b",'CrowdStrike':r"\bCrowdStrike(?:'s)?\b"}
out={}
for f in sorted(glob.glob('*_fool.txt')):
    s=open(f).read();a=s.index('## Full Conference Call Transcript');b=s.index('### Stocks Mentioned');t=s[a:b]
    out[f]={k:len(re.findall(p,t,flags=0 if k in('AI 50+','DRAM / NAND 3+') else re.I)) for k,p in T.items()}
    out[f]['words']=len(t.split())
print(json.dumps(out,indent=1));json.dump(out,open('dell_counts.json','w'),indent=1)
