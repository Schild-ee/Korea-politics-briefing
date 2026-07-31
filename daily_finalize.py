
from __future__ import annotations

from collections import Counter
from datetime import timedelta
from pathlib import Path

from briefing.storage import atomic_save, load_payload
from briefing.utils import iso_kst, now_kst, parse_datetime

DATA_PATH = Path(__file__).with_name("data.json")


def main() -> None:
    payload = load_payload(DATA_PATH)
    now = now_kst()
    target = (now - timedelta(days=1)).date().isoformat()

    issues = []
    for issue in payload.get("issues", []):
        dt = parse_datetime(issue.get("occurredAt"))
        if dt and dt.date().isoformat() == target:
            issue["includedInDailyBrief"] = True
            issues.append(issue)

    domestic = [i for i in issues if i["primaryCategory"] == "국내 정치"]
    foreign = [i for i in issues if i["primaryCategory"] == "외교·대외관계"]

    payload.setdefault("meta", {}).setdefault("dailySummaries", {})[target] = {
        "date": target,
        "finalizedAt": iso_kst(now),
        "total": len(issues),
        "domesticCount": len(domestic),
        "foreignCount": len(foreign),
        "coreCount": sum(i.get("importance") == "핵심" for i in issues),
        "domesticSummary": (
            f"국내 정치 분야에서 {len(domestic)}건의 주요 진전이 확인되었습니다."
            if domestic else "국내 정치 분야의 주요 진전이 확인되지 않았습니다."
        ),
        "foreignSummary": (
            f"외교·대외관계 분야에서 {len(foreign)}건의 주요 진전이 확인되었습니다."
            if foreign else "외교·대외관계 분야의 주요 진전이 확인되지 않았습니다."
        ),
        "issueIds": [i["id"] for i in issues],
    }
    payload["meta"]["lastDailyFinalizedAt"] = iso_kst(now)

    month = target[:7]
    month_issues = [
        issue for issue in payload.get("issues", [])
        if str(issue.get("occurredAt", "")).startswith(month)
    ]
    categories = Counter(i.get("primaryCategory") for i in month_issues)
    subcategories = Counter(i.get("subcategory") for i in month_issues)
    countries = Counter(
        country
        for issue in month_issues
        for country in issue.get("countries", [])
    )
    payload["meta"].setdefault("monthlySummaries", {})[month] = {
        "month": month,
        "updatedAt": iso_kst(now),
        "provisional": now.strftime("%Y-%m") == month,
        "total": len(month_issues),
        "domesticCount": categories.get("국내 정치", 0),
        "foreignCount": categories.get("외교·대외관계", 0),
        "subcategoryCounts": dict(subcategories),
        "countryCounts": dict(countries),
        "coreIssueIds": [
            i["id"] for i in month_issues if i.get("importance") == "핵심"
        ][:10],
    }

    atomic_save(DATA_PATH, payload)
    print(f"Daily brief finalized for {target}: {len(issues)} issues")


if __name__ == "__main__":
    main()
