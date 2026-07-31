from __future__ import annotations
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
import logging
from briefing.config import DATA_PATH,SOURCES,LOOKBACK_HOURS,NAVER_CLIENT_ID,NAVER_CLIENT_SECRET
from briefing.fetchers import fetch_source,fetch_naver
from briefing.classifier import select_item,classify,importance
from briefing.deduplicator import content_hash,find_duplicate
from briefing.summarizer import ai_summary
from briefing.verifier import verify_issue
from briefing.storage import load_data,atomic_save

logging.basicConfig(level=logging.INFO,format='%(levelname)s %(message)s')
KST=ZoneInfo('Asia/Seoul')

def make_id(dt,category,n): return f"{dt.strftime('%Y-%m-%d')}-{'DP' if category=='국내 정치' else 'FR'}-{n:03d}"

def main():
    data=load_data(DATA_PATH); issues=data.setdefault('issues',[]); failed=[]; raw=[]; now=datetime.now(KST); cutoff=now-timedelta(hours=LOOKBACK_HOURS)
    for s in SOURCES:
        if not s.enabled: continue
        try:
            got=fetch_source(s); raw.extend(got); logging.info('%s: %d',s.name,len(got))
        except Exception as e:
            failed.append({'source':s.name,'error':type(e).__name__}); logging.warning('%s failed: %s',s.name,e)
    if NAVER_CLIENT_ID and NAVER_CLIENT_SECRET:
        for q in ('대한민국 국회 정부 정책 선거 수사 판결','대한민국 외교 정상회담 안보 통상 북한'):
            try: raw.extend(fetch_naver(q))
            except Exception as e: failed.append({'source':'네이버 뉴스검색','error':type(e).__name__})
    added=0
    for item in raw:
        try: pub=datetime.fromisoformat(item.published_at)
        except Exception: pub=now
        if pub.astimezone(KST)<cutoff: continue
        if not select_item(item.title,item.text): continue
        primary,related,sub,countries=classify(item.title,item.text,item.source_category)
        summ=ai_summary(item.title,item.text,primary); h=content_hash(item.title,item.text)
        base={
          'id':'','title':summ.get('title') or item.title,'primaryCategory':primary,'relatedCategory':related,'subcategory':sub,
          'countries':countries,'institutions':[item.source_name] if item.official else [],'people':[],
          'importance':importance(item.title,item.text),'status':'공식 발표 확인' if item.official else '확인 중',
          'verificationLevel':'공식 자료 확인' if item.official else '단일 신뢰 출처',
          'occurredAt':item.published_at,'publishedAt':item.published_at,'firstCollectedAt':item.collected_at,'updatedAt':now.isoformat(timespec='seconds'),
          'summary':summ['summary'],'background':summ.get('background',''),'significance':summ.get('significance',''),
          'positions':summ.get('positions',[]),'unverifiedDetails':summ.get('unverifiedDetails',[]),'nextSchedule':summ.get('nextSchedule',''),
          'sources':[{'name':item.source_name,'title':item.title,'date':item.published_at[:10],'url':item.url,'official':item.official}],
          'revisionHistory':[],'corrected':False,'correctionReason':'','relatedIssueIds':[],'includedInDailyBrief':False,'contentHash':h}
        dup=find_duplicate(base,issues)
        if dup:
            known={s.get('url') for s in dup.get('sources',[])}
            for s in base['sources']:
                if s['url'] not in known: dup.setdefault('sources',[]).append(s)
            if len(dup.get('sources',[]))>=2 and dup.get('verificationLevel')!='공식 자료 확인': dup['verificationLevel']='복수 출처 확인'
            dup['updatedAt']=now.isoformat(timespec='seconds'); continue
        seq=1+sum(1 for x in issues if x.get('id','').startswith(now.strftime('%Y-%m-%d')+('-DP' if primary=='국내 정치' else '-FR')))
        base['id']=make_id(now,primary,seq); issues.append(verify_issue(base)); added+=1
    issues.sort(key=lambda x:x.get('updatedAt',''),reverse=True)
    meta=data.setdefault('meta',{}); meta.update({'mode':'live','lastSuccessfulUpdate':now.isoformat(timespec='seconds'),'nextScheduledUpdate':(now+timedelta(minutes=30)).isoformat(timespec='seconds'),'collectionStatus':'정상' if raw else '수집 결과 없음','notice':'공식자료와 신뢰도 높은 보도를 기준으로 자동 갱신됩니다.','sourceCount':len(SOURCES)+(1 if NAVER_CLIENT_ID else 0),'failedSources':failed})
    atomic_save(DATA_PATH,data); logging.info('added=%d total=%d',added,len(issues))
if __name__=='__main__': main()
