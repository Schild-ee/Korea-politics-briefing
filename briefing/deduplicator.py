
from __future__ import annotations

from difflib import SequenceMatcher

from .models import Candidate
from .utils import normalize_title, normalize_url


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def is_duplicate_candidate(candidate: Candidate, seen: list[Candidate]) -> bool:
    url = normalize_url(candidate.url)
    for other in seen:
        if url and url == normalize_url(other.url):
            return True
        if candidate.content_hash and candidate.content_hash == other.content_hash:
            return True
        if similarity(candidate.title, other.title) >= 0.88:
            return True
    return False


def matches_existing_issue(candidate: Candidate, issue: dict) -> bool:
    source_urls = {
        normalize_url(source.get("url", ""))
        for source in issue.get("sources", [])
    }
    if normalize_url(candidate.url) in source_urls:
        return True
    if candidate.content_hash and candidate.content_hash == issue.get("contentHash"):
        return True
    return similarity(candidate.title, issue.get("title", "")) >= 0.9
