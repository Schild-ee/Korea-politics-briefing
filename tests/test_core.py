from pathlib import Path
from briefing.deduplicator import normalize_title,canonical_url,content_hash,is_duplicate
from briefing.classifier import classify,select_item,importance
from briefing.storage import atomic_save,load_data

def test_normalize(): assert normalize_title('[속보] 국회, 법안 의결!')=='국회 법안 의결'
def test_url(): assert 'utm_' not in canonical_url('https://x.test/a?utm_source=z&id=1')
def test_hash(): assert content_hash('a','b')==content_hash('a','b')
def test_classify(): assert classify('한미 정상회담 공동성명','', '외교·대외관계')[0]=='외교·대외관계'
def test_select(): assert select_item('국회 법안 의결','')
def test_importance(): assert importance('대통령 정상회담','')=='핵심'
def test_duplicate():
 a={'title':'국회 주요 법안 의결','primaryCategory':'국내 정치','sources':[{'url':'https://a/x'}]}; b={'title':'국회 주요 법안 의결','primaryCategory':'국내 정치','sources':[{'url':'https://a/x'}]}; assert is_duplicate(a,b)
def test_atomic(tmp_path:Path):
 p=tmp_path/'d.json'; payload={'meta':{},'issues':[{'id':'x','title':'t','primaryCategory':'국내 정치','subcategory':'국회','importance':'주요','status':'공식 발표 확인','verificationLevel':'공식 자료 확인','occurredAt':'2026-01-01T00:00:00+09:00','updatedAt':'2026-01-01T00:00:00+09:00','summary':'s','sources':[{'url':'https://x'}]}]}; atomic_save(p,payload); assert load_data(p)['issues'][0]['id']=='x'
