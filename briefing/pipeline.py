
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from .classifier import (
    classify_category,
    classify_importance,
    classify_subcategory,
    extract_countries,
    extract_institutions,
    is_commentary_only,
    is_relevant,
)
from .config import LOOKBACK_HOURS
from .deduplicator import is_duplicate_candidate, matches_existing_issue
from .models import Candidate, RunStats
from .summarizer import summarize_rule_based
from .utils import iso_kst, now_kst, within_hours
from .verifier import validate_issue


def _issue_id(candidate: Candidate, primary: str, existing_count: int) -> str:
    date = (candidate.published_at or candidate.collected_at)[:10].replace("-", "")
    prefix = "DP" if primary == "국내 정치" else "FR"
    suffix = candidate.content_hash[:8].upper()
    return f"{date}-{prefix}-{suffix}-{existing_count + 1:03d}"


def candidate_to_issue(candidate: Candidate, existing_count: int) -> dict:
    primary, related = classify_category(candidate)
    summary = summarize_rule_based(candidate)
    published = candidate.published_at or candidate.collected_at
    verification = "공식 자료 확인" if candidate.official else "단일 신뢰 출처"
    status = "공식 발표 확인" if candidate.official else "발생"

    issue = {
        "id": _issue_id(candidate, primary, existing_count),
        "title": summary["title"],
        "primaryCategory": primary,
        "relatedCategory": related,
        "subcategory": classify_subcategory(candidate, primary),
        "countries": extract_countries(candidate),
        "institutions": extract_institutions(candidate),
        "people": [],
        "importance": classify_importance(candidate, primary),
        "status": status,
        "verificationLevel": verification,
        "occurredAt": published,
        "publishedAt": published,
        "firstCollectedAt": candidate.collected_at,
        "updatedAt": candidate.collected_at,
        "summary": summary["summary"],
        "background": summary["background"],
        "significance": summary["significance"],
        "positions": [],
        "unverifiedDetails": [],
        "nextSchedule": summary["nextSchedule"],
        "sources": [
            {
                "name": candidate.publisher or candidate.source_name,
                "title": candidate.title,
                "date": published[:10],
                "url": candidate.url,
                "official": candidate.official,
            }
        ],
        "revisionHistory": [],
        "corrected": False,
        "correctionReason": "",
        "relatedIssueIds": [],
        "includedInDailyBrief": False,
        "contentHash": candidate.content_hash,
    }
    validate_issue(issue)
    return issue


def process_candidates(
    candidates: list[Candidate],
    payload: dict,
    stats: RunStats,
) -> None:
    accepted: list[Candidate] = []

    for candidate in candidates:
        if not within_hours(candidate.published_at, LOOKBACK_HOURS):
            stats.rejected_by_date += 1
            continue
        if not is_relevant(candidate):
            stats.rejected_by_relevance += 1
            continue
        if is_commentary_only(candidate):
            stats.rejected_as_commentary += 1
            continue
        if is_duplicate_candidate(candidate, accepted):
            stats.duplicates += 1
            continue
        accepted.append(candidate)

    stats.accepted_candidates = len(accepted)
    existing = payload["issues"]

    for candidate in accepted:
        matched = next(
            (issue for issue in existing if matches_existing_issue(candidate, issue)),
            None,
        )
        if matched:
            source_urls = {source.get("url") for source in matched.get("sources", [])}
            if candidate.url not in source_urls:
                matched.setdefault("revisionHistory", []).append(
                    {
                        "updatedAt": candidate.collected_at,
                        "reason": "새로운 관련 출처 추가",
                        "previousSourceCount": len(matched.get("sources", [])),
                    }
                )
                matched.setdefault("sources", []).append(
                    {
                        "name": candidate.publisher or candidate.source_name,
                        "title": candidate.title,
                        "date": (candidate.published_at or candidate.collected_at)[:10],
                        "url": candidate.url,
                        "official": candidate.official,
                    }
                )
                matched["updatedAt"] = candidate.collected_at
                if candidate.official:
                    matched["verificationLevel"] = "공식 자료 확인"
                    matched["status"] = "공식 발표 확인"
                stats.updated_issues += 1
            else:
                stats.duplicates += 1
            continue

        existing.append(candidate_to_issue(candidate, len(existing)))
        stats.new_issues += 1

    existing.sort(key=lambda item: item.get("updatedAt", ""), reverse=True)
