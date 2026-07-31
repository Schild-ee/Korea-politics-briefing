from __future__ import annotations
from datetime import datetime, timezone
from urllib.parse import urljoin
import html, re, time
import feedparser, requests
from bs4 import BeautifulSoup
from dateutil import parser as dtparser
from .config import REQUEST_TIMEOUT, USER_AGENT, MAX_ITEMS_PER_SOURCE, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
from .models import RawItem

HEADERS={"User-Agent":USER_AGENT,"Accept-Language":"ko-KR,ko;q=0.9,en;q=0.5"}

def now_iso()->str: return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def _get(url:str)->requests.Response:
    last=None
    for wait in (0,2,5):
        if wait: time.sleep(wait)
        try:
            r=requests.get(url,headers=HEADERS,timeout=REQUEST_TIMEOUT)
            r.raise_for_status(); return r
        except requests.RequestException as e: last=e
    raise last or RuntimeError("request failed")

def fetch_rss(source)->list[RawItem]:
    r=_get(source.url); feed=feedparser.parse(r.content); out=[]
    for e in feed.entries[:MAX_ITEMS_PER_SOURCE]:
        title=html.unescape(re.sub(r"<[^>]+>","",e.get("title",""))).strip()
        url=e.get("link","")
        published=e.get("published") or e.get("updated") or now_iso()
        try: published=dtparser.parse(published).astimezone().isoformat(timespec="seconds")
        except Exception: published=now_iso()
        text=BeautifulSoup(e.get("summary","") or e.get("description",""),"html.parser").get_text(" ",strip=True)
        if title and url: out.append(RawItem(source.id,source.name,source.category,title,url,published,now_iso(),text,source.official))
    return out

def fetch_html(source)->list[RawItem]:
    r=_get(source.url); soup=BeautifulSoup(r.text,"html.parser"); out=[]; seen=set()
    # Generic official-board parser: collect likely detail links and nearby date text.
    for a in soup.select('a[href]'):
        title=' '.join(a.get_text(' ',strip=True).split()); href=a.get('href','')
        if len(title)<8 or title in seen: continue
        if not any(k in href for k in ('view.do','View.do','newsId=','seq=','bbs')): continue
        url=urljoin(source.url,href); parent=a.find_parent(['li','tr','div'])
        blob=' '.join(parent.get_text(' ',strip=True).split()) if parent else title
        m=re.search(r'(20\d{2})[.\-/년\s]+(\d{1,2})[.\-/월\s]+(\d{1,2})',blob)
        published=now_iso()
        if m:
            try: published=datetime(int(m.group(1)),int(m.group(2)),int(m.group(3))).astimezone().isoformat(timespec='seconds')
            except Exception: pass
        out.append(RawItem(source.id,source.name,source.category,title,url,published,now_iso(),blob,source.official)); seen.add(title)
        if len(out)>=MAX_ITEMS_PER_SOURCE: break
    return out

def fetch_naver(query:str)->list[RawItem]:
    if not (NAVER_CLIENT_ID and NAVER_CLIENT_SECRET): return []
    r=requests.get('https://openapi.naver.com/v1/search/news.json',params={'query':query,'display':30,'sort':'date'},headers={**HEADERS,'X-Naver-Client-Id':NAVER_CLIENT_ID,'X-Naver-Client-Secret':NAVER_CLIENT_SECRET},timeout=REQUEST_TIMEOUT)
    r.raise_for_status(); out=[]
    for e in r.json().get('items',[]):
        title=BeautifulSoup(e.get('title',''),'html.parser').get_text(' ',strip=True)
        text=BeautifulSoup(e.get('description',''),'html.parser').get_text(' ',strip=True)
        try: pub=dtparser.parse(e.get('pubDate')).astimezone().isoformat(timespec='seconds')
        except Exception: pub=now_iso()
        out.append(RawItem('naver_news','네이버 뉴스검색','국내 정치',title,e.get('originallink') or e.get('link'),pub,now_iso(),text,False))
    return out

def fetch_source(source):
    return fetch_rss(source) if source.source_type=='rss' else fetch_html(source)
