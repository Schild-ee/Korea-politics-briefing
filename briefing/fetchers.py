
from __future__ import annotations

import logging
import os
import time
from email.utils import parsedate_to_datetime
from typing import Iterable

import feedparser
import requests

from .config import (
    MAX_ITEMS_PER_SOURCE,
    NAVER_QUERIES,
    REQUEST_TIMEOUT_SECONDS,
    SOURCES,
    USER_AGENT,
    SourceConfig,
)
from .models import Candidate
from .utils import content_hash, iso_kst, parse_datetime, strip_html

LOGGER = logging.getLogger(__name__)


def _request(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, str | int] | None = None,
    attempts: int = 3,
) -> requests.Response:
    merged = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if headers:
        merged.update(headers)

    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            response = requests.get(
                url,
                headers=merged,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last_error = exc
            if attempt < attempts - 1:
                time.sleep(2 ** attempt)
    assert last_error is not None
    raise last_error


def fetch_google_news(source: SourceConfig) -> list[Candidate]:
    response = _request(source.url)
    parsed = feedparser.parse(response.content)
    if parsed.bozo and not parsed.entries:
        raise ValueError(f"RSS parse failure: {parsed.bozo_exception}")

    collected_at = iso_kst()
    candidates: list[Candidate] = []

    for entry in parsed.entries[:MAX_ITEMS_PER_SOURCE]:
        title = strip_html(entry.get("title", ""))
        url = entry.get("link", "").strip()
        published_raw = entry.get("published") or entry.get("updated") or ""
        published_dt = parse_datetime(published_raw)
        if published_dt is None:
            try:
                published_dt = parsedate_to_datetime(published_raw)
            except (TypeError, ValueError, OverflowError):
                published_dt = None
        published_at = iso_kst(published_dt) if published_dt else ""
        description = strip_html(
            entry.get("summary") or entry.get("description") or ""
        )
        publisher = ""
        source_field = entry.get("source")
        if isinstance(source_field, dict):
            publisher = strip_html(source_field.get("title", ""))

        if not title or not url:
            continue

        candidates.append(
            Candidate(
                source_id=source.id,
                source_name=source.name,
                title=title,
                url=url,
                published_at=published_at,
                collected_at=collected_at,
                description=description,
                category_hint=source.category,
                official=source.official,
                publisher=publisher,
                original_id=str(entry.get("id", url)),
                content_hash=content_hash(title, description, url),
            )
        )
    return candidates


def fetch_naver_news() -> tuple[list[Candidate], str | None]:
    client_id = os.getenv("NAVER_CLIENT_ID", "").strip()
    client_secret = os.getenv("NAVER_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        return [], "disabled: NAVER_CLIENT_ID/NAVER_CLIENT_SECRET not configured"

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }
    collected_at = iso_kst()
    results: list[Candidate] = []

    for query, category in NAVER_QUERIES:
        response = _request(
            "https://openapi.naver.com/v1/search/news.json",
            headers=headers,
            params={"query": query, "display": 50, "sort": "date"},
        )
        payload = response.json()
        for item in payload.get("items", []):
            title = strip_html(item.get("title"))
            description = strip_html(item.get("description"))
            url = item.get("originallink") or item.get("link") or ""
            published = parse_datetime(item.get("pubDate"))
            if not title or not url:
                continue
            results.append(
                Candidate(
                    source_id="naver_news",
                    source_name="네이버 뉴스 검색 API",
                    title=title,
                    url=url,
                    published_at=iso_kst(published) if published else "",
                    collected_at=collected_at,
                    description=description,
                    category_hint=category,
                    official=False,
                    publisher="",
                    original_id=url,
                    content_hash=content_hash(title, description, url),
                )
            )
    return results, None


def fetch_all() -> tuple[list[Candidate], list[dict[str, object]]]:
    all_candidates: list[Candidate] = []
    source_results: list[dict[str, object]] = []

    for source in SOURCES:
        if not source.enabled:
            continue
        try:
            if source.source_type == "google_news_rss":
                items = fetch_google_news(source)
            else:
                raise ValueError(f"unsupported source type: {source.source_type}")
            all_candidates.extend(items)
            source_results.append(
                {
                    "id": source.id,
                    "name": source.name,
                    "status": "success",
                    "count": len(items),
                    "error": "",
                }
            )
        except Exception as exc:  # isolated source failure
            LOGGER.warning("%s failed: %s", source.name, exc)
            source_results.append(
                {
                    "id": source.id,
                    "name": source.name,
                    "status": "failed",
                    "count": 0,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    try:
        naver_items, disabled_reason = fetch_naver_news()
        all_candidates.extend(naver_items)
        source_results.append(
            {
                "id": "naver_news",
                "name": "네이버 뉴스 검색 API",
                "status": "disabled" if disabled_reason else "success",
                "count": len(naver_items),
                "error": disabled_reason or "",
            }
        )
    except Exception as exc:
        LOGGER.warning("Naver News API failed: %s", exc)
        source_results.append(
            {
                "id": "naver_news",
                "name": "네이버 뉴스 검색 API",
                "status": "failed",
                "count": 0,
                "error": f"{type(exc).__name__}: {exc}",
            }
        )

    return all_candidates, source_results
