from __future__ import annotations
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from collections import Counter
from briefing.config import DATA_PATH
from briefing.storage import load_data,atomic_save
KST=ZoneInfo('Asia/Seoul')

def main():
    data=load_data(DATA_PATH); now=datetime.now(KST); day=(now-timedelta(days=1)).date().isoformat()
    items=[i for i in data.get('issues',[]) if str(i.get('occurredAt','')).startswith(day)]
    for i in items: i['includedInDailyBrief']=True
    domestic=[i for i in items if i.get('primaryCategory')=='국내 정치']; foreign=[i for i in items if i.get('primaryCategory')=='외교·대외관계']
    summary={'date':day,'finalizedAt':now.isoformat(timespec='seconds'),'total':len(items),'domesticCount':len(domestic),'foreignCount':len(foreign),'domesticSummary':' '.join(i.get('summary','') for i in domestic[:3]),'foreignSummary':' '.join(i.get('summary','') for i in foreign[:3]),'topIssueIds':[i['id'] for i in sorted(items,key=lambda x:({'핵심':3,'주요':2,'참고':1}.get(x.get('importance'),0)),reverse=True)[:5]]}
    meta=data.setdefault('meta',{}); meta.setdefault('dailySummaries',{})[day]=summary; meta['lastDailyFinalizedAt']=now.isoformat(timespec='seconds')
    month=day[:7]; month_items=[i for i in data.get('issues',[]) if str(i.get('occurredAt','')).startswith(month)]
    meta.setdefault('monthlySummaries',{})[month]={'updatedAt':now.isoformat(timespec='seconds'),'final':now.day==1,'total':len(month_items),'domesticCount':sum(i.get('primaryCategory')=='국내 정치' for i in month_items),'foreignCount':sum(i.get('primaryCategory')=='외교·대외관계' for i in month_items),'importance':dict(Counter(i.get('importance','참고') for i in month_items)),'subcategories':dict(Counter(i.get('subcategory','기타') for i in month_items))}
    atomic_save(DATA_PATH,data)
if __name__=='__main__': main()
