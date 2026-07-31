
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .verifier import validate_payload


def default_payload() -> dict:
    return {
        "meta": {
            "mode": "live",
            "lastSuccessfulUpdate": "",
            "nextScheduledUpdate": "",
            "collectionStatus": "초기화",
            "notice": "공식자료와 신뢰도 높은 보도를 기준으로 자동 갱신됩니다.",
            "lastDailyFinalizedAt": None,
            "sourceCount": 0,
            "failedSources": [],
            "lastRun": {
                "startedAt": "",
                "finishedAt": "",
                "activeSources": 0,
                "fetchedCandidates": 0,
                "acceptedCandidates": 0,
                "duplicates": 0,
                "rejected": 0,
                "rejectedByDate": 0,
                "rejectedByRelevance": 0,
                "rejectedAsCommentary": 0,
                "newIssues": 0,
                "updatedIssues": 0,
                "failedSourceCount": 0,
                "sourceResults": [],
            },
            "dailySummaries": {},
            "monthlySummaries": {},
        },
        "issues": [],
    }


def load_payload(path: Path) -> dict:
    if not path.exists():
        return default_payload()
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.setdefault("meta", {})
    payload.setdefault("issues", [])
    return payload


def atomic_save(path: Path, payload: dict) -> None:
    validate_payload(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
