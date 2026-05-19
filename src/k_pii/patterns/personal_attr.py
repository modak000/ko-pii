"""인적 속성 (Personal Attributes) — 학력·전공·직책·측정치.

검출 카테고리:
- ``EDUCATION`` (OGG_EDUCATION) : 대학교/전문대 (사전 매칭)
- ``MAJOR``     (FD_MAJOR)      : 전공·학과 (사전 + suffix 정규화)
- ``POSITION``  (CV_POSITION)   : 직책·직급 (titles 사전, 단독 emit)
- ``AGE``       (QT_AGE)         : 32세 / 32살
- ``HEIGHT``    (QT_LENGTH)      : 175cm / 1.75m
- ``WEIGHT``    (QT_WEIGHT)      : 70kg / 70kilo

위험도 정책:
- EDUCATION, MAJOR: MEDIUM/LOW (quasi-identifier)
- POSITION: LOW (단독은 직책일 뿐)
- AGE/HEIGHT/WEIGHT: INFO (단독 PII 아님, 결합위험도 산정용)

Legal basis: 개인정보보호법 제2조; 「개인정보 비식별 조치 가이드라인」
준식별자 (Quasi-Identifier) 분류 — 다른 정보와 결합 시 재식별 위험.
"""
from __future__ import annotations

import re
from typing import Iterator

from k_pii.core.types import DetectionResult, RiskLevel

LEGAL_BASIS = "개인정보보호법 제2조"


# ═══════════════════════════════════════════════════════════════════════
# EDUCATION (학력)
# ═══════════════════════════════════════════════════════════════════════
_EDUCATION_PATTERN = re.compile(
    r"(?<![가-힣A-Za-z])"
    r"([가-힣]{2,15}(?:대학교|대학|대학원대학교|전문대학|대학원)|"
    r"KAIST|POSTECH|UNIST|GIST|DGIST|"
    r"카이스트|포스텍|유니스트|지스트|디지스트)"
    r"(?![가-힣])"
)


def detect_education(text: str) -> Iterator[DetectionResult]:
    from k_pii.dictionaries.universities import (
        ALL_UNIVERSITIES, UNIVERSITY_ABBREV, is_university, normalize_university,
    )
    for m in _EDUCATION_PATTERN.finditer(text):
        raw = m.group(1)
        if not is_university(raw):
            # 접미사 변형 ("대학교" 끝) 도 시도
            continue
        canonical = normalize_university(raw)
        yield DetectionResult(
            label="EDUCATION",
            text=raw,
            start=m.start(1),
            end=m.end(1),
            risk_level=RiskLevel.MEDIUM,
            confidence=0.95,
            evidence=["pattern:education", f"canonical:{canonical}"],
            legal_basis=LEGAL_BASIS,
            extra={"category": "준식별자", "canonical": canonical},
        )


# ═══════════════════════════════════════════════════════════════════════
# MAJOR (전공)
# ═══════════════════════════════════════════════════════════════════════
# "컴퓨터공학과", "경영학부", "법학", "의예과" 등 — 짧은 전공 ("수학"·"법학") 도 허용
_MAJOR_PATTERN = re.compile(
    r"(?<![가-힣A-Za-z])"
    r"([가-힣]{1,11}(?:학과|학부|전공|학|과))"
    r"(?![가-힣A-Za-z])"
)


def detect_major(text: str) -> Iterator[DetectionResult]:
    from k_pii.dictionaries.majors import is_major, normalize_major
    seen: set[tuple[int, int]] = set()
    for m in _MAJOR_PATTERN.finditer(text):
        raw = m.group(1)
        if not is_major(raw):
            continue
        span = (m.start(1), m.end(1))
        if span in seen:
            continue
        seen.add(span)
        canonical = normalize_major(raw)
        yield DetectionResult(
            label="MAJOR",
            text=raw,
            start=span[0],
            end=span[1],
            risk_level=RiskLevel.LOW,
            confidence=0.9,
            evidence=["pattern:major", f"canonical:{canonical}"],
            legal_basis=LEGAL_BASIS,
            extra={"category": "준식별자", "canonical": canonical},
        )


# ═══════════════════════════════════════════════════════════════════════
# POSITION (직책)
# ═══════════════════════════════════════════════════════════════════════
# titles 사전을 사용 — 단독 직책 emit (PERSON 컨텍스트와 별개)
# *키워드 anchor 필수* — "직급:" "직책:" "직위:" 등이 5자 이내 앞에 있어야
# 단독 emit. 이게 없으면 PERSON 검출에서 직책 인접 단서로만 사용됨.
_POSITION_ANCHORS = ("직급", "직책", "직위", "보직", "직군")
_POSITION_PATTERN = re.compile(
    r"(?<![가-힣A-Za-z])"
    r"([가-힣]{1,6})"
    r"(?![가-힣A-Za-z])"
)


def _position_anchor_before(text: str, start: int, window: int = 12) -> str | None:
    head = text[max(0, start - window): start]
    for kw in _POSITION_ANCHORS:
        if kw in head:
            return kw
    return None


def detect_position(text: str) -> Iterator[DetectionResult]:
    from k_pii.dictionaries.titles import is_title, title_domain
    seen: set[tuple[int, int]] = set()
    for m in _POSITION_PATTERN.finditer(text):
        raw = m.group(1)
        if not is_title(raw):
            continue
        kw = _position_anchor_before(text, m.start(1))
        if kw is None:
            continue
        span = (m.start(1), m.end(1))
        if span in seen:
            continue
        seen.add(span)
        domain = title_domain(raw) or "unknown"
        yield DetectionResult(
            label="POSITION",
            text=raw,
            start=span[0],
            end=span[1],
            risk_level=RiskLevel.LOW,
            confidence=0.85,
            evidence=["pattern:position", f"keyword:{kw}", f"domain:{domain}"],
            legal_basis=LEGAL_BASIS,
            extra={"category": "준식별자", "domain": domain},
        )


# ═══════════════════════════════════════════════════════════════════════
# AGE / HEIGHT / WEIGHT (측정치)
# ═══════════════════════════════════════════════════════════════════════
_AGE_PATTERN = re.compile(
    r"(?<![0-9])"
    r"(\d{1,3})"
    r"\s*(?:세|살)"
    r"(?![가-힣])"
)

_HEIGHT_PATTERN = re.compile(
    r"(?<![0-9.])"
    r"(\d{2,3}(?:\.\d{1,2})?)"
    r"\s*(?:cm|센티(?:미터)?|㎝)"
    r"(?![A-Za-z])",
    re.IGNORECASE,
)

# 키 (m 단위): 1.75m / 1m75 — 위험은 일반 거리와 충돌
_HEIGHT_M_PATTERN = re.compile(
    r"(?<![0-9.])"
    r"(1\.\d{1,2})\s*m"
    r"(?![A-Za-z])"
)

_WEIGHT_PATTERN = re.compile(
    r"(?<![0-9.])"
    r"(\d{1,3}(?:\.\d{1,2})?)"
    r"\s*(?:kg|키로(?:그램)?|킬로(?:그램)?|㎏|kilogram)"
    r"(?![A-Za-z])",
    re.IGNORECASE,
)


def detect_measurements(text: str) -> Iterator[DetectionResult]:
    for m in _AGE_PATTERN.finditer(text):
        age = int(m.group(1))
        if 0 <= age <= 150:
            yield DetectionResult(
                label="AGE", text=m.group(0),
                start=m.start(), end=m.end(),
                risk_level=RiskLevel.INFO, confidence=0.95,
                evidence=["pattern:age", f"value:{age}"],
                legal_basis=LEGAL_BASIS,
                extra={"category": "준식별자", "value": age, "unit": "year"},
            )

    for m in _HEIGHT_PATTERN.finditer(text):
        height = float(m.group(1))
        if 50 <= height <= 250:
            yield DetectionResult(
                label="HEIGHT", text=m.group(0),
                start=m.start(), end=m.end(),
                risk_level=RiskLevel.INFO, confidence=0.9,
                evidence=["pattern:height", f"value:{height}cm"],
                legal_basis=LEGAL_BASIS,
                extra={"category": "준식별자", "value": height, "unit": "cm"},
            )

    for m in _HEIGHT_M_PATTERN.finditer(text):
        height_m = float(m.group(1))
        if 0.5 <= height_m <= 2.5:
            yield DetectionResult(
                label="HEIGHT", text=m.group(0),
                start=m.start(), end=m.end(),
                risk_level=RiskLevel.INFO, confidence=0.85,
                evidence=["pattern:height_m", f"value:{height_m}m"],
                legal_basis=LEGAL_BASIS,
                extra={"category": "준식별자", "value": height_m * 100, "unit": "cm"},
            )

    for m in _WEIGHT_PATTERN.finditer(text):
        weight = float(m.group(1))
        if 1 <= weight <= 300:
            yield DetectionResult(
                label="WEIGHT", text=m.group(0),
                start=m.start(), end=m.end(),
                risk_level=RiskLevel.INFO, confidence=0.9,
                evidence=["pattern:weight", f"value:{weight}kg"],
                legal_basis=LEGAL_BASIS,
                extra={"category": "준식별자", "value": weight, "unit": "kg"},
            )


# ═══════════════════════════════════════════════════════════════════════
# 통합 detect 진입점
# ═══════════════════════════════════════════════════════════════════════
def detect(text: str) -> Iterator[DetectionResult]:
    """모든 인적 속성 카테고리 검출."""
    yield from detect_education(text)
    yield from detect_major(text)
    yield from detect_position(text)
    yield from detect_measurements(text)
