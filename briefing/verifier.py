
from __future__ import annotations

from datetime import datetime

ALLOWED_CATEGORIES = {"국내 정치", "외교·대외관계"}
ALLOWED_IMPORTANCE = {"핵심", "주요", "참고"}
ALLOWED_STATUS = {"발생", "확인 중", "공식 발표 확인", "후속 진행", "내용 수정", "종결"}
ALLOWED_VERIFICATION = {"공식 자료 확인", "복수 출처 확인", "단일 신뢰 출처", "확인 중"}


def validate_issue(issue: dict) -> None:
    required = (
        "id", "title", "primaryCategory", "subcategory", "importance",
        "status", "verificationLevel", "occurredAt", "updatedAt",
        "summary", "sources", "contentHash",
    )
    for field in required:
        if field not in issue:
            raise ValueError(f"missing issue field: {field}")
    if issue["primaryCategory"] not in ALLOWED_CATEGORIES:
        raise ValueError("invalid primaryCategory")
    if issue["importance"] not in ALLOWED_IMPORTANCE:
        raise ValueError("invalid importance")
    if issue["status"] not in ALLOWED_STATUS:
        raise ValueError("invalid status")
    if issue["verificationLevel"] not in ALLOWED_VERIFICATION:
        raise ValueError("invalid verificationLevel")
    if not issue["title"].strip() or not issue["summary"].strip():
        raise ValueError("empty title or summary")
    if not isinstance(issue["sources"], list) or not issue["sources"]:
        raise ValueError("issue must contain at least one source")
    for field in ("occurredAt", "updatedAt"):
        datetime.fromisoformat(issue[field])


def validate_payload(payload: dict) -> None:
    if not isinstance(payload.get("meta"), dict):
        raise ValueError("meta must be object")
    if not isinstance(payload.get("issues"), list):
        raise ValueError("issues must be array")
    for issue in payload["issues"]:
        validate_issue(issue)
