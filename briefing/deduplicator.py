from __future__ import annotations
import hashlib,re
from difflib import SequenceMatcher
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode

def normalize_title(s:str)->str:
    s=re.sub(r'\[[^\]]+\]|\([^)]*자료[^)]*\)',' ',s)
    s=re.sub(r'[^0-9A-Za-z가-힣 ]+',' ',s)
    return ' '.join(s.lower().split())

def canonical_url(url:str)->str:
    p=urlsplit(url); q=[(k,v) for k,v in parse_qsl(p.query) if not k.lower().startswith(('utm_','fbclid','gclid'))]
    return urlunsplit((p.scheme.lower(),p.netloc.lower(),p.path.rstrip('/'),urlencode(q),''))

def content_hash(title:str,text:str)->str:
    return hashlib.sha256((normalize_title(title)+'\n'+' '.join(text.split())[:4000]).encode()).hexdigest()

def is_duplicate(a:dict,b:dict)->bool:
    au={canonical_url(x.get('url','')) for x in a.get('sources',[])}; bu={canonical_url(x.get('url','')) for x in b.get('sources',[])}
    if au & bu: return True
    ratio=SequenceMatcher(None,normalize_title(a.get('title','')),normalize_title(b.get('title',''))).ratio()
    return ratio>=0.78 and a.get('primaryCategory')==b.get('primaryCategory')

def find_duplicate(candidate:dict,issues:list[dict]):
    for issue in issues:
        if candidate.get('contentHash') and candidate['contentHash']==issue.get('contentHash'): return issue
        if is_duplicate(candidate,issue): return issue
    return None
