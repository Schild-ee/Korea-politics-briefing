
from datetime import timedelta
from pathlib import Path

import pytest

from briefing.classifier import (
    classify_category,
    classify_subcategory,
    is_commentary_only,
    is_relevant,
)
from briefing.deduplicator import is_duplicate_candidate
from briefing.models import Candidate, RunStats
from briefing.pipeline import process_candidates
from briefing.storage import atomic_save, default_payload, load_payload
from briefing.utils import content_hash, iso_kst, normalize_title, normalize_url, now_kst


def candidate(title: str, url: str = "https://example.com/a", category: str = "국내 정치"):
    return Candidate(
        source_id="test",
        source_name="test",
        title=title,
        url=url,
        published_at=iso_kst(now_kst() - timedelta(hours=1)),
        collected_at=iso_kst(),
        description="정부가 관련 정책을 확정하고 시행 계획을 발표했다.",
        category_hint=category,
        official=True,
        content_hash=content_hash(title, url),
    )


def test_normalization():
    assert normalize_title("[속보] 국회, 법안 통과") == "국회 법안 통과"
    assert normalize_url("HTTPS://Example.COM/a/?x=1") == "https://example.com/a"


def test_content_hash_stable():
    assert content_hash("A", "B") == content_hash("A", "B")


def test_domestic_classification():
    c = candidate("국회, 주요 법안 본회의 통과")
    assert classify_category(c)[0] == "국내 정치"
    assert classify_subcategory(c, "국내 정치") == "국회"


def test_foreign_classification():
    c = candidate("한미 정상회담 공동성명 발표", category="외교·대외관계")
    assert classify_category(c)[0] == "외교·대외관계"


def test_commentary_rejected():
    c = candidate("야당, 정부 정책 맹비난")
    c.description = "야당이 정부를 비판했다."
    assert is_commentary_only(c)


def test_relevant_action():
    assert is_relevant(candidate("정부, 정책 시행 확정"))


def test_duplicate_url():
    a = candidate("정부 정책 확정")
    b = candidate("다른 제목", url=a.url)
    assert is_duplicate_candidate(b, [a])


def test_pipeline_adds_issue():
    payload = default_payload()
    stats = RunStats()
    process_candidates([candidate("국회, 법안 본회의 통과")], payload, stats)
    assert stats.new_issues == 1
    assert len(payload["issues"]) == 1


def test_zero_new_reason_counters():
    payload = default_payload()
    stats = RunStats()
    old = candidate("오래된 정치 기사")
    old.published_at = "2020-01-01T00:00:00+09:00"
    process_candidates([old], payload, stats)
    assert stats.new_issues == 0
    assert stats.rejected_by_date == 1


def test_atomic_save(tmp_path: Path):
    path = tmp_path / "data.json"
    payload = default_payload()
    atomic_save(path, payload)
    loaded = load_payload(path)
    assert loaded["issues"] == []


def test_failed_save_preserves_original(tmp_path: Path):
    path = tmp_path / "data.json"
    payload = default_payload()
    atomic_save(path, payload)
    bad = {"meta": {}, "issues": [{"title": "bad"}]}
    with pytest.raises(ValueError):
        atomic_save(path, bad)
    assert load_payload(path)["issues"] == []
