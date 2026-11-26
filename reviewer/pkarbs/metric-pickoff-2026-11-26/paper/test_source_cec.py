"""Planted checks for source_cec (each can fail)."""
import json, os, tempfile, sys
import source_cec as S
bad = []
def ck(c, m):
    if not c: bad.append(m)
doc = {'data': [{'cand_name': '蔣萬安', 'party_name': '中國國民黨', 'is_victor': '*'}, {'cand_name': '沈伯洋', 'party_name': '民主進步黨', 'is_victor': ' '}]}
ck(S.elected_name(doc) == '蔣萬安', 'one elected -> name')
doc2 = {'data': [{'cand_name': 'A', 'is_victor': '*'}, {'cand_name': 'B', 'is_victor': '*'}]}
ck(S.elected_name(doc2) is None, 'two elected -> None')
ck(S.elected_name({'data': [{'cand_name': 'A', 'is_victor': ''}]}) is None, 'none elected -> None')
d = tempfile.mkdtemp()
json.dump({'tp': 'u1', 'np': 'u2'}, open(os.path.join(d, 'cec_urls.json'), 'w'))
json.dump({'tp': {'蔣萬安': 'Chiang Wan-an', '沈伯洋': 'Puma Shen'}, 'np': {'李四川': 'Lee Shu-chuan'}}, open(os.path.join(d, 'cec_names.json'), 'w'))
evs = {'tp': [{'title': 'Chiang Wan-an'}, {'title': 'Puma Shen'}], 'np': [{'title': 'Lee Shu-chuan'}]}
docs = {'u1': doc, 'u2': {'data': [{'cand_name': '某人', 'is_victor': '*'}]}}
src = S.Source(evs, d, fetcher=lambda u: docs[u])
out = src.poll()
ck(out == [('tp', 'Chiang Wan-an', None, {'cec_name': '蔣萬安', 'url': 'u1'})], 'tp fires Chiang; np (unknown name) fires nothing: %s' % out)
json.dump({'tp': {'蔣萬安': 'Chiang W.'}}, open(os.path.join(d, 'cec_names.json'), 'w'))
try:
    S.Source(evs, d, fetcher=lambda u: docs[u]); ck(False, 'mapping to a non-existent title must raise')
except ValueError:
    pass
print('FAIL: ' + '; '.join(bad) if bad else 'PASS (5 checks)'); sys.exit(1 if bad else 0)
