import sys; sys.path.insert(0,'live/netflix')
from pull_netflix import us_rows
S=["country_name\tcountry_iso2\tweek\tcategory\tweekly_rank\tshow_title\tseason_title\tcumulative_weeks_in_top_10\n",
"United States\tUS\t2026-10-04\tFilms\t1\tA\tN/A\t2\n","Canada\tCA\t2026-10-04\tFilms\t1\tB\tN/A\t1\n","United States\tUS\t2026-10-04\tTV\t1\tC\tC: Season 1\t3\n"]
r=list(us_rows(S)); ok=[len(r)==3, r[1][5]=='A', r[2][5]=='C', r[0][0]=='country_name']
print(sum(ok),'of 4 checks pass')
