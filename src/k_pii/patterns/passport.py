"""여권번호 (Korean Passport Number) detection.

Format: 1-2 uppercase letter prefix + 8 digits.

Prefix codes (외교부 발급 분류):
  M  - 일반 여권 (general)
  S  - 일반 여권 (newer issuance)
  G  - 일반 여권 (newer)
  O  - 관용 여권 (official)
  D  - 외교관 여권 (diplomatic)
  R  - 여행증명서 (refugee/emergency travel doc)
  PM/PS/PO - newer compound prefixes occasionally seen

There is no publicly documented checksum, so detection relies on the prefix
pattern + 8-digit suffix.

Legal basis: 개인정보보호법 시행령 제19조 (고유식별정보 — 여권번호).
"""
from __future__ import annotations

import re
from typing import Iterator

from k_pii.core.types import DetectionResult, RiskLevel

LABEL = "PASSPORT"
LEGAL_BASIS = "개인정보보호법 시행령 제19조"
CATEGORY = "고유식별정보"

_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])"
    r"(M|S|G|O|D|R|PM|PS|PO)"
    r"([0-9]{8})"
    r"(?![A-Za-z0-9])"
)


def detect(text: str) -> Iterator[DetectionResult]:
    for m in _PATTERN.finditer(text):
        prefix = m.group(1)
        number = m.group(2)
        yield DetectionResult(
            label=LABEL,
            text=m.group(0),
            start=m.start(),
            end=m.end(),
            risk_level=RiskLevel.CRITICAL,
            confidence=0.9,
            evidence=["pattern:passport", f"prefix:{prefix}"],
            legal_basis=LEGAL_BASIS,
            extra={
                "prefix": prefix,
                "number": number,
                "category": CATEGORY,
            },
        )
