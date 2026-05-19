"""생년월일 (Date of Birth) detection.

지원 포맷:
  - 1988년 1월 1일 / 1988년 01월 01일
  - 1988.1.1 / 1988.01.01 / 1988-01-01 / 1988/01/01
  - 88년 1월 1일 / 88.1.1 (2자리 연도)
  - 880101 (RRN 앞 6자리 — 키워드 anchor 필수)
  - 88년생 / 1988년생

검증:
  - 연도: 1900 ~ 현재 년도
  - 월: 1-12
  - 일: 1-31 (월별 + 윤년 검증)

키워드 anchor (단순 날짜 vs 생년월일 구분):
  - "생년월일" / "생일" / "출생" / "출생일" / "DOB" / "Date of Birth"
  - "년생" suffix (88년생 = 1988년생)
  - 키워드 없는 단순 날짜 (예: "2024년 4월 15일 회의") 는 검출 안 함

Legal basis: 개인정보보호법 제2조; 생년월일은 RRN 앞자리와 동일하여
강한 식별성을 가짐. 다른 정보와 결합 시 즉시 식별 가능 = quasi-identifier.
"""
from __future__ import annotations

import re
from datetime import date
from typing import Iterator

from k_pii.core.types import DetectionResult, RiskLevel

LABEL = "DT_BIRTH"
LEGAL_BASIS = "개인정보보호법 제2조"
CATEGORY = "준식별자"

# 한국어 키워드 anchor — 25자 윈도우
_KEYWORDS = (
    "생년월일", "생일", "출생일", "출생", "태어난",
    "DOB", "Date of Birth", "Birth Date", "birthday",
)

# 패턴 1: YYYY년 M월 D일 / YYYY년 MM월 DD일
_PATTERN_KOREAN = re.compile(
    r"(?<![0-9])"
    r"(\d{4}|\d{2})"
    r"\s*년\s*"
    r"(\d{1,2})"
    r"\s*월\s*"
    r"(\d{1,2})"
    r"\s*일"
)

# 패턴 2: YYYY.M.D / YYYY-MM-DD / YYYY/MM/DD / YY.MM.DD (구분자 통일)
_PATTERN_NUMERIC = re.compile(
    r"(?<![0-9])"
    r"(\d{2,4})"
    r"([./-])"
    r"(\d{1,2})"
    r"\2"
    r"(\d{1,2})"
    r"(?![0-9])"
)

# 패턴 3: YY년생 / YYYY년생 (연도만)
_PATTERN_BIRTH_YEAR = re.compile(
    r"(?<![0-9])"
    r"(\d{2,4})"
    r"\s*년\s*생"
)


def _normalize_year(year: int) -> int | None:
    """2자리 연도를 4자리로 정규화. 1900 ~ 현재년도 범위만 허용."""
    current_year = date.today().year
    if year < 100:
        # 2자리: 25 이하면 20XX, 그 이상은 19XX
        year = 2000 + year if year <= current_year % 100 else 1900 + year
    if 1900 <= year <= current_year:
        return year
    return None


def _valid_date(year: int, month: int, day: int) -> bool:
    """월/일 + 윤년 검증."""
    try:
        date(year, month, day)
        return True
    except ValueError:
        return False


def _has_keyword_before(text: str, start: int, window: int = 25) -> str | None:
    head = text[max(0, start - window): start]
    for kw in _KEYWORDS:
        if kw in head:
            return kw
    return None


def _has_birth_marker_after(text: str, end: int) -> bool:
    """패턴 매치 끝 뒤에 '생' (예: "88년생") 이 붙어있는지."""
    tail = text[end: end + 2]
    return tail.startswith("생")


def detect(text: str) -> Iterator[DetectionResult]:
    seen: set[tuple[int, int]] = set()

    # 패턴 1: 한국어 (YYYY년 M월 D일)
    for m in _PATTERN_KOREAN.finditer(text):
        year_raw = int(m.group(1))
        year = _normalize_year(year_raw)
        if year is None:
            continue
        month, day = int(m.group(2)), int(m.group(3))
        if not _valid_date(year, month, day):
            continue
        kw = _has_keyword_before(text, m.start())
        if kw is None and not _has_birth_marker_after(text, m.end()):
            continue  # 단순 날짜 (회의·작성일 등) — 거부
        span = (m.start(), m.end())
        seen.add(span)
        yield DetectionResult(
            label=LABEL,
            text=m.group(0),
            start=m.start(),
            end=m.end(),
            risk_level=RiskLevel.HIGH,
            confidence=0.95,
            evidence=[
                "pattern:birth_korean",
                f"date:{year}-{month:02d}-{day:02d}",
                f"keyword:{kw}" if kw else "marker:생",
            ],
            legal_basis=LEGAL_BASIS,
            extra={
                "year": year, "month": month, "day": day,
                "format": "korean", "category": CATEGORY,
            },
        )

    # 패턴 2: 숫자 구분자 (YYYY.M.D)
    for m in _PATTERN_NUMERIC.finditer(text):
        span = (m.start(), m.end())
        if any(span[0] < e and s < span[1] for s, e in seen):
            continue
        year = _normalize_year(int(m.group(1)))
        if year is None:
            continue
        month, day = int(m.group(3)), int(m.group(4))
        if not _valid_date(year, month, day):
            continue
        kw = _has_keyword_before(text, m.start())
        if kw is None:
            continue  # 숫자 날짜는 키워드 anchor 필수
        seen.add(span)
        yield DetectionResult(
            label=LABEL,
            text=m.group(0),
            start=m.start(),
            end=m.end(),
            risk_level=RiskLevel.HIGH,
            confidence=0.9,
            evidence=[
                "pattern:birth_numeric",
                f"date:{year}-{month:02d}-{day:02d}",
                f"keyword:{kw}",
            ],
            legal_basis=LEGAL_BASIS,
            extra={
                "year": year, "month": month, "day": day,
                "format": "numeric", "category": CATEGORY,
            },
        )

    # 패턴 3: YY년생 (연도만, "생" marker 자체가 anchor)
    for m in _PATTERN_BIRTH_YEAR.finditer(text):
        span = (m.start(), m.end())
        if any(span[0] < e and s < span[1] for s, e in seen):
            continue
        year = _normalize_year(int(m.group(1)))
        if year is None:
            continue
        seen.add(span)
        yield DetectionResult(
            label=LABEL,
            text=m.group(0),
            start=m.start(),
            end=m.end(),
            risk_level=RiskLevel.MEDIUM,
            confidence=0.85,
            evidence=["pattern:birth_year_only", f"year:{year}", "marker:년생"],
            legal_basis=LEGAL_BASIS,
            extra={
                "year": year, "format": "year_only", "category": CATEGORY,
            },
        )
