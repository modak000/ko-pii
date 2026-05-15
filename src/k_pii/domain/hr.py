"""인사 도메인 — 사번·직번·교번 등 내부 식별자.

추가 검출:
- 공무원 사번 (예: ``2023-12345`` — "사번"/"공무원번호" 키워드 anchor 필요)
- 교번 (교사·교수) — "교번" 키워드 anchor

CLAUDE.md §8 의 "공무원 직책 사전 세분화" 는 사용자 도메인 입력이 필요해
별도 기능으로 분리. 본 모듈은 키워드 anchor 기반 단순 룰.

Legal basis: 개인정보보호법 제2조; 국가공무원법 제22조.
"""
from __future__ import annotations

import re
from typing import Iterator

from k_pii.core.types import DetectionResult, RiskLevel

LABEL = "EMPLOYEE_ID"
LEGAL_BASIS = "개인정보보호법 제2조; 국가공무원법 제22조"
CATEGORY = "일반개인정보"

_KEYWORDS = ("사번", "공무원번호", "교번", "직원번호", "임용번호")

_PATTERN = re.compile(
    r"(?<![0-9])"
    r"(\d{4,12})"
    r"(?![0-9])"
)


def _keyword_before(text: str, start: int, window: int = 15) -> str | None:
    head = text[max(0, start - window): start]
    for kw in _KEYWORDS:
        if kw in head:
            return kw
    return None


def detect(text: str) -> Iterator[DetectionResult]:
    for m in _PATTERN.finditer(text):
        kw = _keyword_before(text, m.start())
        if kw is None:
            continue
        yield DetectionResult(
            label=LABEL,
            text=m.group(1),
            start=m.start(),
            end=m.end(),
            risk_level=RiskLevel.MEDIUM,
            confidence=0.85,
            evidence=["pattern:employee_id", f"keyword:{kw}", "domain:hr"],
            legal_basis=LEGAL_BASIS,
            extra={
                "category": CATEGORY,
                "domain": "hr",
                "value": m.group(1),
            },
        )
