
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Candidate:
    source_id: str
    source_name: str
    title: str
    url: str
    published_at: str
    collected_at: str
    description: str
    category_hint: str
    official: bool
    publisher: str = ""
    original_id: str = ""
    content_hash: str = ""

    def searchable_text(self) -> str:
        return f"{self.title} {self.description} {self.publisher}".strip()


@dataclass
class RunStats:
    started_at: str = ""
    finished_at: str = ""
    active_sources: int = 0
    fetched_candidates: int = 0
    rejected_by_date: int = 0
    rejected_by_relevance: int = 0
    rejected_as_commentary: int = 0
    duplicates: int = 0
    accepted_candidates: int = 0
    new_issues: int = 0
    updated_issues: int = 0
    failed_source_count: int = 0
    source_results: list[dict[str, Any]] = field(default_factory=list)

    @property
    def rejected(self) -> int:
        return (
            self.rejected_by_date
            + self.rejected_by_relevance
            + self.rejected_as_commentary
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "startedAt": self.started_at,
            "finishedAt": self.finished_at,
            "activeSources": self.active_sources,
            "fetchedCandidates": self.fetched_candidates,
            "acceptedCandidates": self.accepted_candidates,
            "duplicates": self.duplicates,
            "rejected": self.rejected,
            "rejectedByDate": self.rejected_by_date,
            "rejectedByRelevance": self.rejected_by_relevance,
            "rejectedAsCommentary": self.rejected_as_commentary,
            "newIssues": self.new_issues,
            "updatedIssues": self.updated_issues,
            "failedSourceCount": self.failed_source_count,
            "sourceResults": self.source_results,
        }
