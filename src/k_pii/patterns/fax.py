"""팩스번호 (FAX) 검출 — 전화번호와 분리.

포맷 자체는 일반전화 (서울/지역/070) 와 동일하지만, "팩스", "FAX", "fax" 등의
키워드가 5~15 자 이내 앞에 있을 때만 PHONE 이 아닌 FAX 로 분류한다.

Legal basis: 개인정보보호법 제2조.
"""
from __future__ import annotations

import re
from typing import Iterator

from k_pii.core.types import DetectionResult, RiskLevel

LABEL = "FAX"
LEGAL_BASIS = "개인정보보호법 제2조"
CATEGORY = "일반개인정보"

_PATTERN = re.compile(
    r"(?<![0-9+])"
    r"(0\d{1,2})"
    r"[-.\s]?"
    r"(\d{3,4})"
    r"[-.\s]?"
    r"(\d{4})"
    r"(?![0-9])"
)

_KEYWORDS = ("팩스", "FAX", "fax", "Fax", "F.", "전송")


def _has_keyword_before(text: str, start: int, window: int = 12) -> str | None:
    head = text[max(0, start - window): start]
    for kw in _KEYWORDS:
        if kw in head:
            return kw
    return None


def detect(text: str) -> Iterator[DetectionResult]:
    for m in _PATTERN.finditer(text):
        kw = _has_keyword_before(text, m.start())
        if kw is None:
            continue
        yield DetectionResult(
            label=LABEL,
            text=m.group(0),
            start=m.start(),
            end=m.end(),
            risk_level=RiskLevel.LOW,
            confidence=0.85,
            evidence=["pattern:fax", f"keyword:{kw}"],
            legal_basis=LEGAL_BASIS,
            extra={
                "prefix": m.group(1),
                "digits_only": re.sub(r"\D", "", m.group(0)),
                "category": CATEGORY,
            },
        )
