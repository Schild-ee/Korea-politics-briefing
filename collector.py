
from __future__ import annotations

import json
import logging
from datetime import timedelta
from pathlib import Path

from briefing.fetchers import fetch_all
from briefing.models import RunStats
from briefing.pipeline import process_candidates
from briefing.storage import atomic_save, load_payload
from briefing.utils import iso_kst, now_kst

DATA_PATH = Path(__file__).with_name("data.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
)


def print_report(payload: dict, stats: RunStats, saved: bool) -> None:
    print("COLLECTOR START")
    print(f"Run started: {stats.started_at}")
    print(f"Active sources: {stats.active_sources}")
    for result in stats.source_results:
        if result["status"] == "success":
            print(f"Source {result['name']}: {result['count']} candidates")
        else:
            print(
                f"Source {result['name']}: {result['status']} - "
                f"{result.get('error', '')}"
            )
    print(f"Fetched candidates: {stats.fetched_candidates}")
    print(f"Rejected by date: {stats.rejected_by_date}")
    print(f"Rejected by relevance: {stats.rejected_by_relevance}")
    print(f"Rejected as commentary: {stats.rejected_as_commentary}")
    print(f"Duplicates: {stats.duplicates}")
    print(f"Accepted: {stats.accepted_candidates}")
    print(f"New issues: {stats.new_issues}")
    print(f"Updated issues: {stats.updated_issues}")
    print(f"Total issues in data.json: {len(payload.get('issues', []))}")
    print(f"Saved: {'yes' if saved else 'no'}")
    if stats.new_issues == 0:
        print("No new issues added.")
        print("Reason:")
        print(f"- {stats.duplicates} duplicates")
        print(f"- {stats.rejected_by_date} outside date range")
        print(f"- {stats.rejected_by_relevance} low relevance")
        print(f"- {stats.rejected_as_commentary} commentary only")
    print(f"Run finished: {stats.finished_at}")
    print("COLLECTOR END")


def main() -> None:
    stats = RunStats(started_at=iso_kst())
    payload = load_payload(DATA_PATH)
    candidates, source_results = fetch_all()

    stats.source_results = source_results
    stats.active_sources = sum(
        result["status"] in {"success", "failed"} for result in source_results
    )
    stats.failed_source_count = sum(
        result["status"] == "failed" for result in source_results
    )
    stats.fetched_candidates = len(candidates)

    process_candidates(candidates, payload, stats)

    finished = now_kst()
    stats.finished_at = iso_kst(finished)
    failed_sources = [
        {
            "id": result["id"],
            "name": result["name"],
            "error": result["error"],
        }
        for result in source_results
        if result["status"] == "failed"
    ]

    successful_sources = sum(
        result["status"] == "success" for result in source_results
    )
    if successful_sources == 0:
        status = "실패"
        notice = "모든 출처 수집에 실패하여 마지막 정상 데이터를 유지했습니다."
    elif failed_sources:
        status = "부분 성공"
        notice = "일부 출처 수집에 실패했으며 성공한 출처 결과만 반영했습니다."
    elif stats.new_issues == 0 and stats.updated_issues == 0:
        status = "정상·신규 없음"
        notice = "수집은 정상 완료됐으나 이번 실행에서는 신규 이슈가 없었습니다."
    else:
        status = "정상"
        notice = "공식자료와 신뢰도 높은 보도를 기준으로 자동 갱신됩니다."

    meta = payload.setdefault("meta", {})
    meta.update(
        {
            "mode": "live",
            "lastSuccessfulUpdate": (
                stats.finished_at
                if successful_sources > 0
                else meta.get("lastSuccessfulUpdate", "")
            ),
            "nextScheduledUpdate": iso_kst(finished + timedelta(minutes=30)),
            "collectionStatus": status,
            "notice": notice,
            "sourceCount": successful_sources,
            "failedSources": failed_sources,
            "lastRun": stats.as_dict(),
        }
    )
    meta.setdefault("lastDailyFinalizedAt", None)
    meta.setdefault("dailySummaries", {})
    meta.setdefault("monthlySummaries", {})

    saved = False
    # Preserve the prior file if every active source failed.
    if successful_sources > 0:
        atomic_save(DATA_PATH, payload)
        saved = True

    print_report(payload, stats, saved)


if __name__ == "__main__":
    main()
