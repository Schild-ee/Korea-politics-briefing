"""
정치·외교 브리핑 자동 수집기 연결용 골격.

현재는 data.json의 메타데이터만 갱신합니다.
실제 운영 시 공식 RSS/API 또는 허용된 데이터 소스를 연결하고,
검증·중복 제거·분류·요약 후 issues 배열을 갱신해야 합니다.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json

DATA_PATH = Path(__file__).with_name("data.json")
KST = timezone(timedelta(hours=9))


def main() -> None:
    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    now = datetime.now(KST)
    payload["meta"]["lastSuccessfulUpdate"] = now.isoformat(timespec="seconds")
    payload["meta"]["nextScheduledUpdate"] = (
        now + timedelta(minutes=30)
    ).isoformat(timespec="seconds")

    # TODO:
    # 1. 공식 RSS/API 확인
    # 2. 신규 자료 정규화
    # 3. 중복 이슈 판별
    # 4. 국내 정치 / 외교·대외관계 분류
    # 5. 공식 자료 검증 및 요약
    # 6. issues 배열 갱신

    DATA_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("data.json metadata updated")


if __name__ == "__main__":
    main()
