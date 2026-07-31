
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote_plus


@dataclass(frozen=True)
class SourceConfig:
    id: str
    name: str
    source_type: str
    url: str
    category: str
    official: bool
    enabled: bool = True
    priority: int = 1


def google_news_url(query: str) -> str:
    return (
        "https://news.google.com/rss/search?q="
        + quote_plus(query)
        + "&hl=ko&gl=KR&ceid=KR:ko"
    )


# Direct official-list pages that repeatedly timed out in GitHub Actions are not
# enabled by default. The default path uses Google News RSS searches restricted
# to official government domains. This is a discovery layer; each item retains
# the originating source label and URL.
SOURCES: tuple[SourceConfig, ...] = (
    SourceConfig(
        id="official_domestic",
        name="공식기관 국내정치 검색 피드",
        source_type="google_news_rss",
        url=google_news_url(
            '(site:president.go.kr OR site:assembly.go.kr OR site:korea.kr '
            'OR site:nec.go.kr OR site:ccourt.go.kr OR site:scourt.go.kr) '
            '(의결 OR 확정 OR 임명 OR 지명 OR 사퇴 OR 발의 OR 통과 OR 공포 '
            'OR 시행 OR 영장 OR 기소 OR 판결 OR 선거 OR 국무회의)'
        ),
        category="국내 정치",
        official=True,
        priority=1,
    ),
    SourceConfig(
        id="official_foreign",
        name="공식기관 외교안보 검색 피드",
        source_type="google_news_rss",
        url=google_news_url(
            '(site:president.go.kr OR site:mofa.go.kr OR site:unikorea.go.kr '
            'OR site:mnd.go.kr OR site:motir.go.kr OR site:korea.kr) '
            '(정상회담 OR 외교장관 OR 공동성명 OR 협정 OR 합의 OR 제재 '
            'OR 안보 OR 북한 OR 북핵 OR 통상협상 OR 재외국민)'
        ),
        category="외교·대외관계",
        official=True,
        priority=1,
    ),
    SourceConfig(
        id="reliable_domestic_news",
        name="국내 정치 주요 보도 검색 피드",
        source_type="google_news_rss",
        url=google_news_url(
            '대한민국 정치 (국회 OR 대통령실 OR 정부 OR 선거 OR 법안 OR 판결) '
            '(의결 OR 확정 OR 임명 OR 기소 OR 판결 OR 시행)'
        ),
        category="국내 정치",
        official=False,
        priority=2,
    ),
    SourceConfig(
        id="reliable_foreign_news",
        name="외교·안보 주요 보도 검색 피드",
        source_type="google_news_rss",
        url=google_news_url(
            '대한민국 외교 안보 (정상회담 OR 공동성명 OR 협정 OR 북한 OR 북핵 '
            'OR 통상협상 OR 제재 OR 재외국민)'
        ),
        category="외교·대외관계",
        official=False,
        priority=2,
    ),
)

NAVER_QUERIES: tuple[tuple[str, str], ...] = (
    ("대통령실 국회 정부 법안 선거 인사 판결", "국내 정치"),
    ("대한민국 외교 정상회담 북한 북핵 통상협상", "외교·대외관계"),
)

REQUEST_TIMEOUT_SECONDS = 25
LOOKBACK_HOURS = 72
MAX_ITEMS_PER_SOURCE = 50
USER_AGENT = (
    "KoreaPoliticsBriefingBot/2.0 "
    "(GitHub Actions; respectful public-feed reader)"
)
