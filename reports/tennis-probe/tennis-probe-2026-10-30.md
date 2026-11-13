# Tennis score-source probe — 2026-10-30

UA: `pkarbs-research/1.0 (contact nm@delphic.co)`. One curl each, no retries.

| URL | status | bytes | first 200 bytes |
|---|---|---|---|
| https://www.atptour.com/en/scores/current | 403 | 5488 | <!DOCTYPE html><html lang="en-US"><head><title>Just a moment...</title><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=Edge"><meta nam |
| https://www.wtatennis.com/ | 200 | 450903 | <!DOCTYPE html> <html lang="en"> <head>     <meta charset="UTF-8">     <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">     <meta name="viewport" content="width=device-width, initial-sca |
| https://www.flashscore.com/ | 200 | 733106 | <!DOCTYPE html> <html lang="en">     <head>         <meta charset="utf-8">         <title>Football Live Scores, Latest Football Results | Flashscore.com</title>         <script defer src="https://cdn. |
| https://www.livescore.com/ | 301 | 0 | <no body: > |
| https://www.espn.com/tennis/scoreboard | 403 | 919 | <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"> <HTML><HEAD><META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=iso-8859-1"> <TITLE>ERROR |
| https://www.tennisabstract.com/ | 200 | 68332 |  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "https://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> <html xmlns="https://www.w3.org/1999/xhtml"> <head> <title>Tennis Abstract:  |
| https://www.ultimatetennisstatistics.com/ | 200 | 32964 | <!DOCTYPE html> <html>          <head> 	 	 	 	 	 	<meta charset="utf-8"/> 	<meta name="viewport" content="width=device-width, initial-scale=1"/> 	<title>Ultimate Tennis Statistics</ |
| https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/README.md | 404 | 14 | 404: Not Found |

## Verdict
**PASS** — report written with one row per URL (status, bytes, first 200 B). 403/301/404 are recorded results, not task failures per the task definition.

## Notes for rn1 matching
- WTA (200, 450 KB) and Flashscore (200, 733 KB) return full HTML; tennisabstract (200) and ultimatetennisstatistics (200) too. **atptour 403 (Cloudflare), ESPN tennis scoreboard 403, livescore 301.** Sackmann raw README 404 (repo path changed).

## Cleanup
`/tmp/tennis_body` and `/tmp/tennis_url` removed. No curls left running (all `timeout 30`).
- `ps` (own procs): none of the probe's curls remain. Logger pid 2951556 still up (unrelated).
- `free -m`:
               total        used        free      shared  buff/cache   available
Mem:            7746        3593         385           4        4079        4152
Swap:           4095        3116         979
