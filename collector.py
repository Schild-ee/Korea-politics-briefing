"""
자동 수집기 연결용 골격.
실제 운영 시 공식 RSS/API 또는 허용된 데이터 소스를 연결하고,
검증·중복 제거 후 data.json을 갱신하세요.
"""
from pathlib import Path
import json
from datetime import datetime, timezone, timedelta

DATA = Path(__file__).with_name("data.json")
KST = timezone(timedelta(hours=9))

def main():
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    payload["meta"]["lastSuccessfulUpdate"] = datetime.now(KST).isoformat(timespec="seconds")
    # TODO: 공식 출처/API 수집 → 정규화 → 중복 판별 → 검증 → issues 갱신
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("data.json metadata updated")

if __name__ == "__main__":
    main()
