from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any

ALLOWED_CATEGORIES={"국내 정치","외교·대외관계"}
ALLOWED_IMPORTANCE={"핵심","주요","참고"}
ALLOWED_STATUS={"발생","확인 중","공식 발표 확인","후속 진행","내용 수정","종결"}
ALLOWED_VERIFICATION={"공식 자료 확인","복수 출처 확인","단일 신뢰 출처","확인 중"}

@dataclass
class RawItem:
    source_id:str; source_name:str; source_category:str; title:str; url:str
    published_at:str; collected_at:str; text:str=""; official:bool=True

@dataclass
class Issue:
    id:str; title:str; primaryCategory:str; relatedCategory:str=""; subcategory:str="기타 국내 정치"
    countries:list[str]=field(default_factory=list); institutions:list[str]=field(default_factory=list); people:list[str]=field(default_factory=list)
    importance:str="참고"; status:str="확인 중"; verificationLevel:str="확인 중"
    occurredAt:str=""; publishedAt:str=""; firstCollectedAt:str=""; updatedAt:str=""
    summary:str=""; background:str=""; significance:str=""; positions:list[Any]=field(default_factory=list)
    unverifiedDetails:list[str]=field(default_factory=list); nextSchedule:str=""; sources:list[dict[str,Any]]=field(default_factory=list)
    revisionHistory:list[dict[str,Any]]=field(default_factory=list); corrected:bool=False; correctionReason:str=""
    relatedIssueIds:list[str]=field(default_factory=list); includedInDailyBrief:bool=False; contentHash:str=""
    def to_dict(self): return asdict(self)

def validate_issue(d:dict)->None:
    required=["id","title","primaryCategory","subcategory","importance","status","verificationLevel","occurredAt","updatedAt","summary","sources"]
    missing=[k for k in required if k not in d]
    if missing: raise ValueError(f"missing fields: {missing}")
    if d["primaryCategory"] not in ALLOWED_CATEGORIES: raise ValueError("invalid category")
    if d["importance"] not in ALLOWED_IMPORTANCE: raise ValueError("invalid importance")
    if d["status"] not in ALLOWED_STATUS: raise ValueError("invalid status")
    if d["verificationLevel"] not in ALLOWED_VERIFICATION: raise ValueError("invalid verification")
