from __future__ import annotations
import re

FOREIGN=['외교','정상회담','회담','미국','중국','일본','북한','러시아','유엔','국제','안보','국방','통상','관세','협정','제재','재외국민','대사','외교부','통일부','북핵','미사일']
DOMESTIC=['국회','법안','본회의','상임위','대통령실','국무회의','정부','정당','선거','공천','인사','임명','사퇴','수사','기소','영장','판결','헌법재판','대법원','예산']
ACTION=['의결','확정','발표','지명','임명','사퇴','해임','발의','통과','가결','부결','공포','시행','착수','압수수색','청구','발부','기각','기소','선고','체결','합의','개최','방문','제재','결정','승인']
EXCLUDE=['논평','비판','촉구','주장','공방','반발','칼럼','사설','인터뷰']
COUNTRIES=['미국','중국','일본','북한','러시아','우크라이나','유럽연합','EU','인도','베트남','필리핀','이란','이스라엘','유엔','UN']

def select_item(title:str,text:str)->bool:
    s=title+' '+text
    if any(x in title for x in EXCLUDE) and not any(a in s for a in ACTION): return False
    return any(a in s for a in ACTION)

def classify(title:str,text:str,source_category:str):
    s=title+' '+text
    fs=sum(s.count(x) for x in FOREIGN); ds=sum(s.count(x) for x in DOMESTIC)
    primary='외교·대외관계' if fs>ds else source_category
    related='국내 정치' if primary=='외교·대외관계' and ds>1 else ('외교·대외관계' if primary=='국내 정치' and fs>1 else '')
    if primary=='외교·대외관계':
        if '정상' in s: sub='정상외교'
        elif any(x in s for x in ['북한','남북']): sub='남북관계'
        elif any(x in s for x in ['국방','군사','안보','미사일']): sub='국방·안보'
        elif any(x in s for x in ['통상','관세','수출','무역','공급망']): sub='통상·경제외교'
        elif any(x in s for x in ['유엔','국제기구','다자']): sub='다자외교'
        else: sub='양자외교'
    else:
        if any(x in s for x in ['국회','법안','본회의','상임위']): sub='국회'
        elif any(x in s for x in ['선거','공천','후보']): sub='선거'
        elif any(x in s for x in ['기소','영장','수사','판결','재판']): sub='수사·재판'
        elif any(x in s for x in ['임명','지명','사퇴','해임','인사']): sub='인사'
        elif '대통령' in s: sub='대통령실'
        elif any(x in s for x in ['정당','여당','야당']): sub='정당'
        else: sub='정부·정책'
    countries=[c for c in COUNTRIES if c in s]
    return primary,related,sub,countries

def importance(title:str,text:str)->str:
    s=title+' '+text
    core=['대통령','국무총리','본회의','헌법재판','대법원','정상회담','공동성명','군사 충돌','탄핵','계엄','장관 임명','기소','구속영장']
    if any(x in s for x in core): return '핵심'
    return '주요' if len(s)>100 or any(a in s for a in ACTION) else '참고'
