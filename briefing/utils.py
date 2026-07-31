
from __future__ import annotations

import hashlib
import html
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup
from dateutil import parser as date_parser

KST = timezone(timedelta(hours=9))


def now_kst() -> datetime:
    return datetime.now(KST)


def iso_kst(value: datetime | None = None) -> str:
    dt = value or now_kst()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=KST)
    return dt.astimezone(KST).isoformat(timespec="seconds")


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = date_parser.parse(value)
    except (ValueError, TypeError, OverflowError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=KST)
    return dt.astimezone(KST)


def strip_html(value: str | None) -> str:
    if not value:
        return ""
    raw = html.unescape(value)
    if "<" not in raw and ">" not in raw:
        return re.sub(r"\s+", " ", raw).strip()
    soup = BeautifulSoup(raw, "html.parser")
    return re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()


def normalize_title(value: str) -> str:
    text = strip_html(value).lower()
    text = re.sub(r"\[[^\]]+\]|\([^)]+\)$", " ", text)
    text = re.sub(r"[^0-9a-z가-힣]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_url(value: str) -> str:
    if not value:
        return ""
    parts = urlsplit(value.strip())
    path = re.sub(r"/+$", "", parts.path)
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, "", ""))


def content_hash(*values: str) -> str:
    normalized = "||".join(normalize_title(v) for v in values if v)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def within_hours(value: str, hours: int, reference: datetime | None = None) -> bool:
    dt = parse_datetime(value)
    if dt is None:
        return False
    ref = reference or now_kst()
    return ref - timedelta(hours=hours) <= dt <= ref + timedelta(minutes=10)
