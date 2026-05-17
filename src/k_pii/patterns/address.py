"""주소 (Korean address) detection — 도로명 + 지번.

도로명(road-name) 주소: 로·길·대로 + 건물번호.
지번(jibun) 주소:        동·읍·면·리 + 번지(번지수).

To keep precision high without a full 행정구역 dictionary, we require *either*:
  - A 시/도/시/군/구 token immediately before the road/dong component, OR
  - A "주소" keyword within 20 characters before the match.

Detail components such as 동/호/층 inside parentheses are not parsed in
detail (kept in the matched span if adjacent).

Legal basis: 개인정보보호법 제2조 (거주지 식별 가능 정보).
"""
from __future__ import annotations

import re
from typing import Iterator

from k_pii.core.types import DetectionResult, RiskLevel

LABEL = "ADDRESS"
LEGAL_BASIS = "개인정보보호법 제2조"
CATEGORY = "일반개인정보"

# Optional 시·도 + 0~2 시·군·구 (성남시 분당구 같은 2단계) + road + 번지
_PATTERN_ROAD = re.compile(
    r"(?:([가-힣]+(?:특별시|광역시|특별자치도|특별자치시|도))\s+)?"
    r"((?:[가-힣]+(?:시|군|구)\s+){0,2})"
    r"([가-힣A-Za-z0-9]+(?:대로|로|길))"
    r"\s+"
    r"([0-9]+(?:-[0-9]+)?)"
)

# 지번 주소: 동/읍/면/리 + 번지수 (0~2 시·군·구 허용)
_PATTERN_JIBUN = re.compile(
    r"(?:([가-힣]+(?:특별시|광역시|특별자치도|특별자치시|도))\s+)?"
    r"((?:[가-힣]+(?:시|군|구)\s+){0,2})"
    r"([가-힣]+(?:동|읍|면|리))"
    r"\s+"
    r"([0-9]+(?:-[0-9]+)?)"
    r"(?:\s*번지)?"
)


def _has_anchor(text: str, start: int, city: str | None, district: str | None) -> str | None:
    if city or district:
        return "prefix"
    window_start = max(0, start - 20)
    if "주소" in text[window_start:start]:
        return "keyword"
    return None


def detect(text: str) -> Iterator[DetectionResult]:
    seen: set[tuple[int, int]] = set()

    from k_pii.dictionaries.districts import is_province

    for m in _PATTERN_ROAD.finditer(text):
        city = m.group(1)
        districts = (m.group(2) or "").strip()
        # 시·도 prefix 가 있다면 *실제 한국 17개 광역지자체* 인지 검증
        # ("바티스타밤이라도" 같은 한글 단어가 "...도" 끝난다고 매칭되는 것 거부)
        if city and not is_province(city):
            continue
        anchor = _has_anchor(text, m.start(), city, districts)
        if anchor is None:
            continue
        span = (m.start(), m.end())
        seen.add(span)
        yield DetectionResult(
            label=LABEL,
            text=m.group(0).strip(),
            start=m.start(),
            end=m.end(),
            risk_level=RiskLevel.MEDIUM,
            confidence=0.8,
            evidence=["pattern:address_road", f"anchor:{anchor}"],
            legal_basis=LEGAL_BASIS,
            extra={
                "format": "road_name",
                "city": city,
                "districts": districts,
                "road": m.group(3),
                "building_number": m.group(4),
                "category": CATEGORY,
            },
        )

    for m in _PATTERN_JIBUN.finditer(text):
        span = (m.start(), m.end())
        if any(span[0] < e and s < span[1] for s, e in seen):
            continue  # already claimed by road pattern
        city = m.group(1)
        districts = (m.group(2) or "").strip()
        # 시·도 prefix 검증 (위와 동일 — "바티스타밤이라도" 거부)
        if city and not is_province(city):
            continue
        anchor = _has_anchor(text, m.start(), city, districts)
        if anchor is None:
            continue
        seen.add(span)
        yield DetectionResult(
            label=LABEL,
            text=m.group(0).strip(),
            start=m.start(),
            end=m.end(),
            risk_level=RiskLevel.MEDIUM,
            confidence=0.75,
            evidence=["pattern:address_jibun", f"anchor:{anchor}"],
            legal_basis=LEGAL_BASIS,
            extra={
                "format": "jibun",
                "city": city,
                "districts": districts,
                "dong": m.group(3),
                "lot_number": m.group(4),
                "category": CATEGORY,
            },
        )
