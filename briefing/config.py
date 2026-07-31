from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data.json"
KST_NAME = "Asia/Seoul"
USER_AGENT = "KoreaPoliticsBriefingBot/1.0 (+public GitHub project; respectful polling)"
REQUEST_TIMEOUT = 20
LOOKBACK_HOURS = int(os.getenv("LOOKBACK_HOURS", "48"))
MAX_ITEMS_PER_SOURCE = int(os.getenv("MAX_ITEMS_PER_SOURCE", "30"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")

@dataclass(frozen=True)
class Source:
    id: str
    name: str
    category: str
    source_type: str
    url: str
    official: bool = True
    enabled: bool = True
    priority: int = 1

SOURCES = [
    Source("korea_press", "대한민국 정책브리핑", "국내 정치", "html", "https://www.korea.kr/briefing/pressReleaseList.do"),
    Source("mofa_press", "대한민국 외교부", "외교·대외관계", "html", "https://www.mofa.go.kr/www/brd/m_4080/list.do"),
    Source("official_domestic_feed", "공식기관 국내정치 검색 피드", "국내 정치", "rss", "https://news.google.com/rss/search?q=%28site%3Aassembly.go.kr+OR+site%3Apresident.go.kr+OR+site%3Anec.go.kr+OR+site%3Accourt.go.kr+OR+site%3Ascourt.go.kr+OR+site%3Aopm.go.kr%29+when%3A2d&hl=ko&gl=KR&ceid=KR%3Ako", True, True, 2),
    Source("official_foreign_feed", "공식기관 외교안보 검색 피드", "외교·대외관계", "rss", "https://news.google.com/rss/search?q=%28site%3Amofa.go.kr+OR+site%3Amnd.go.kr+OR+site%3Aunikorea.go.kr+OR+site%3Amotir.go.kr%29+when%3A2d&hl=ko&gl=KR&ceid=KR%3Ako", True, True, 2),
]
