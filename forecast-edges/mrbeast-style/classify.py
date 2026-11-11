import json,re,collections
E=json.load(open('/tmp/w/allev.json'))
FAM=[('MrBeast views day N (main)',r'views of (next )?MrBeast video( on)? day|MrBeast video day|next MrBeast video day'),
('MrBeast views week N (main)',r'views of (next )?MrBeast video (on )?week|MrBeast video week'),
('MrBeast Gaming views',r'MrBeast Gaming video|MrBeast Gaming'),
('MrBeast channel milestones (subs/views by month)',r'MrBeast (hit|reach)|MrBeast.*subscribers|MrBeast.*Billion views'),
('MrBeast say-words',r'MrBeast say'),
('MrBeast other (raise $, one-offs)',r'MrBeast|Beast Games'),
('Other YouTube video views (GTA VI, Ronaldo, halftime)',r'# of views|# Views|views on|views of'),
('Netflix weekly #N / top (global+US, movie+show)',r'Netflix'),
('Spotify weekly #N song / charts / artist',r'Spotify'),
('Billboard Hot 100 / album weekly',r'Billboard'),
('Apple App Store #N free/paid',r'App Store'),
('Podcast/mention words (Rogan, All-In, Lemonade, TV eps)',r'What will be said|say during|say in|say on|will say'),
('Trump/Elon Truth Social/X post counts',r'Truth Social|will Trump post|will Elon|tweets|posts'),
('OpenRouter / AI model rankings',r'OpenRouter|AI lab|AI model'),
('Rotten Tomatoes score',r'Rotten Tomatoes'),
('Box office (opening/weekend/total)',r'Box Office|box office|domestic gross|grossing'),
('Google searches / trends',r'Google|Searched'),
('Twitch/stream viewers/Kai/Speed',r'Twitch|Kai |Speed|stream|Stream|viewer|Viewer|Viewership'),
('TikTok',r'TikTok')]
def fam(t):
    for n,r in FAM:
        if re.search(r,t): return n
    return 'other'
if __name__=='__main__':
    g=collections.defaultdict(list)
    for e in E.values(): g[fam(e['title'])].append(e)
    for n,v in sorted(g.items(),key=lambda kv:-sum(float(x['vol'] or 0) for x in kv[1])):
        ends=sorted(x['end'][:10] for x in v if x.get('end'))
        print(f"{n}|{len(v)}|${sum(float(x['vol'] or 0) for x in v)/1e6:.1f}M|{ends[0] if ends else ''}..{ends[-1] if ends else ''}")
