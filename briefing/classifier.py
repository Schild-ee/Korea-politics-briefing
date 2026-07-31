
from __future__ import annotations

import re
from collections import Counter

from .models import Candidate

ACTION_TERMS = {
    "의결", "확정", "통과", "공포", "시행", "발의", "상정", "임명", "지명",
    "사퇴", "해임", "기소", "구속", "영장", "압수수색", "판결", "선고",
    "결정", "개최", "합의", "공동성명", "협정", "타결", "제재", "발표",
    "승인", "채택", "출범", "개편", "회담", "조치", "체결",
}

COMMENTARY_TERMS = {
    "비판", "반발", "공방", "논평", "주장", "촉구", "맹비난", "설전",
    "말싸움", "정쟁", "인터뷰", "칼럼", "사설", "전망", "관측",
}

POLITICAL_TERMS = {
    "대통령", "대통령실", "국회", "정부", "국무회의", "정당", "여당",
    "야당", "선거", "법안", "예산", "장관", "총리", "검찰", "경찰",
    "공수처", "법원", "헌법재판소", "대법원", "정책", "인사",
}

FOREIGN_TERMS = {
    "외교", "정상회담", "외교장관", "국방", "안보", "북한", "북핵",
    "남북", "통상", "협정", "공동성명", "국제기구", "유엔", "제재",
    "재외국민", "대사", "양자회담", "다자회의", "공급망",
}

COUNTRY_PATTERNS = {
    "미국": ("미국", "한미", "워싱턴"),
    "중국": ("중국", "한중", "베이징"),
    "일본": ("일본", "한일", "도쿄"),
    "북한": ("북한", "남북", "평양", "북핵"),
    "러시아": ("러시아", "한러", "모스크바"),
    "유럽연합": ("유럽연합", "EU"),
    "유엔": ("유엔", "UN"),
}

SUBCATEGORY_RULES = (
    ("정상외교", ("정상회담", "정상외교", "대통령 방문")),
    ("양자외교", ("외교장관회담", "양자회담", "대사")),
    ("다자외교", ("다자", "G7", "G20", "APEC", "아세안")),
    ("국방·안보", ("국방", "연합훈련", "군사", "안보")),
    ("남북관계", ("남북", "통일부")),
    ("북핵", ("북핵", "핵실험", "미사일")),
    ("통상·경제외교", ("통상", "FTA", "관세", "무역협상")),
    ("경제안보", ("공급망", "경제안보", "핵심광물")),
    ("국제기구", ("유엔", "UN", "국제기구")),
    ("국제제재", ("제재", "독자제재")),
    ("재외국민", ("재외국민", "교민", "철수")),
    ("대통령실", ("대통령실", "대통령")),
    ("국회", ("국회", "본회의", "상임위원회", "법안")),
    ("정당", ("정당", "여당", "야당", "당대표")),
    ("정부·정책", ("정부", "국무회의", "정책", "부처")),
    ("선거", ("선거", "공천", "후보")),
    ("인사", ("임명", "지명", "인사", "사퇴", "해임")),
    ("예산", ("예산", "추경")),
    ("수사·재판", ("수사", "검찰", "경찰", "기소", "영장", "압수수색")),
    ("헌법·사법", ("헌법재판소", "대법원", "판결", "선고")),
)


def is_relevant(candidate: Candidate) -> bool:
    text = candidate.searchable_text()
    has_action = any(term in text for term in ACTION_TERMS)
    has_domain = any(term in text for term in POLITICAL_TERMS | FOREIGN_TERMS)
    # Official-domain discovery feeds are already tightly scoped, but still
    # require either an action term or a strong domain term.
    return has_domain and (has_action or candidate.official)


def is_commentary_only(candidate: Candidate) -> bool:
    text = candidate.searchable_text()
    commentary = sum(term in text for term in COMMENTARY_TERMS)
    actions = sum(term in text for term in ACTION_TERMS)
    return commentary > 0 and actions == 0


def classify_category(candidate: Candidate) -> tuple[str, str]:
    text = candidate.searchable_text()
    foreign_score = sum(term in text for term in FOREIGN_TERMS)
    domestic_score = sum(term in text for term in POLITICAL_TERMS)

    if candidate.category_hint == "외교·대외관계":
        foreign_score += 2
    else:
        domestic_score += 2

    primary = "외교·대외관계" if foreign_score > domestic_score else "국내 정치"
    related = ""
    if foreign_score >= 2 and domestic_score >= 2:
        related = "국내 정치" if primary == "외교·대외관계" else "외교·대외관계"
    return primary, related


def classify_subcategory(candidate: Candidate, primary: str) -> str:
    text = candidate.searchable_text()
    for name, keywords in SUBCATEGORY_RULES:
        if any(keyword in text for keyword in keywords):
            if primary == "외교·대외관계" and name in {
                "정상외교", "양자외교", "다자외교", "국방·안보",
                "남북관계", "북핵", "통상·경제외교", "경제안보",
                "국제기구", "국제제재", "재외국민",
            }:
                return name
            if primary == "국내 정치" and name in {
                "대통령실", "국회", "정당", "정부·정책", "선거",
                "인사", "예산", "수사·재판", "헌법·사법",
            }:
                return name
    return "기타 대외관계" if primary == "외교·대외관계" else "기타 국내 정치"


def classify_importance(candidate: Candidate, primary: str) -> str:
    text = candidate.searchable_text()
    core_terms = {
        "대통령", "국무총리", "본회의 통과", "헌법재판소", "대법원",
        "정상회담", "공동성명", "군사충돌", "선거 결과", "장관 임명",
        "구속영장", "기소", "국제제재",
    }
    major_terms = ACTION_TERMS
    if any(term in text for term in core_terms):
        return "핵심"
    if any(term in text for term in major_terms):
        return "주요"
    return "참고"


def extract_countries(candidate: Candidate) -> list[str]:
    text = candidate.searchable_text()
    return [
        country
        for country, patterns in COUNTRY_PATTERNS.items()
        if any(pattern in text for pattern in patterns)
    ]


def extract_institutions(candidate: Candidate) -> list[str]:
    text = candidate.searchable_text()
    institutions = [
        name for name in (
            "대통령실", "대한민국 국회", "외교부", "국방부", "통일부",
            "헌법재판소", "대법원", "검찰", "경찰청", "중앙선거관리위원회",
        )
        if name.replace("대한민국 ", "") in text
    ]
    if candidate.publisher and candidate.publisher not in institutions:
        institutions.append(candidate.publisher)
    return institutions[:8]
