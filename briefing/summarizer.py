
from __future__ import annotations

import re

from .models import Candidate
from .utils import strip_html


def _sentences(text: str) -> list[str]:
    clean = re.sub(r"\s+", " ", strip_html(text)).strip()
    if not clean:
        return []
    parts = re.split(r"(?<=[.!?。])\s+|(?<=다\.)\s+", clean)
    return [part.strip() for part in parts if len(part.strip()) >= 15]


def summarize_rule_based(candidate: Candidate) -> dict[str, str]:
    sentences = _sentences(candidate.description)
    summary_parts = sentences[:2]
    if not summary_parts:
        summary_parts = [candidate.title]
    summary = " ".join(summary_parts)
    if len(summary) > 500:
        summary = summary[:497].rstrip() + "..."

    return {
        "title": candidate.title.strip(),
        "summary": summary,
        "background": "",
        "significance": (
            "공식 발표 또는 신뢰도 높은 보도의 핵심 조치와 후속 절차를 "
            "기준으로 지속 확인이 필요한 사안이다."
        ),
        "nextSchedule": "",
    }
