// Test for feeds/preflight_pmdota.sh against a mock gamma/CLOB: modes inwin -> exit 0, old -> exit 2 (UNVERIFIED), empty -> exit 1. Usage: node test_preflight_pmdota.js inwin|old|empty
const http=require('http'),{spawnSync}=require('child_process');
let tick=0;const mk=(id,s)=>({conditionId:id,question:'Dota 2: X vs Y - Game 1 Winner',outcomes:'["A","B"]',clobTokenIds:JSON.stringify(['t'+id+'a','t'+id+'b']),gameStartTime:s,sportsMarketType:'moneyline'});
const mode=process.argv[2];
const srv=http.createServer((q,r)=>{const u=new URL(q.url,'http://x');r.setHeader('content-type','application/json');
 if(u.pathname==='/events'){const s=mode==='inwin'?new Date(Date.now()+300000).toISOString():'2026-11-19T10:00:00Z';const off=+u.searchParams.get('offset')||0;r.end(JSON.stringify(off===0&&mode!=='empty'?[{markets:[mk('Q1',s)]}]:[]));}
 else{tick++;r.end(JSON.stringify({bids:[{price:'0.4',size:String(tick)}],asks:[{price:'0.6',size:'5'}]}));}});
srv.listen(0,()=>{const p=srv.address().port;
 const {spawn}=require('child_process');let out='';const c=spawn('bash',[require('path').join(__dirname,'preflight_pmdota.sh'),'10'],{env:{...process.env,GAMMA_URL:'http://127.0.0.1:'+p,CLOB_URL:'http://127.0.0.1:'+p}});c.stdout.on('data',d=>out+=d);c.on('exit',code=>{ const o={stdout:out,status:code};
 console.log(mode,'->',o.stdout.trim().split('\n').slice(0,-1).join(' | '),'EXIT',o.status);srv.close();});});
