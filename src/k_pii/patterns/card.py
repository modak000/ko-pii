"""신용카드 / 체크카드 번호 (Card Number) detection.

Detection requires the Luhn (mod-10) checksum to pass. Supports common card
lengths (13–19 digits) with optional hyphen or space separators.

Legal status: 카드번호 자체가 개인정보로 분류되는지는 사용 맥락에 따라 달라지나,
실명·계좌·기타 식별 정보와 결합 시 개인을 식별할 수 있어 보수적으로 HIGH로 보고.
"""
from __future__ import annotations

import re
from typing import Iterator

from k_pii.checksum.luhn import is_valid as is_valid_luhn
from k_pii.core.types import DetectionResult, RiskLevel

LABEL = "CARD"
LEGAL_BASIS = "개인정보보호법 제2조; 여신전문금융업법"
CATEGORY = "일반개인정보"

# Two accepted shapes:
#   1. Four 4-digit groups separated by hyphens or spaces (4-4-4-(1..7))
#   2. A bare 13–19 digit run with no separators
_PATTERN = re.compile(
    r"(?<![0-9])"
    r"(?:"
    r"[0-9]{4}[- ][0-9]{4}[- ][0-9]{4}[- ][0-9]{1,7}"
    r"|"
    r"[0-9]{13,19}"
    r")"
    r"(?![0-9])"
)


def detect(text: str) -> Iterator[DetectionResult]:
    for m in _PATTERN.finditer(text):
        raw = m.group(0)
        digits = re.sub(r"[- ]", "", raw)
        if not (13 <= len(digits) <= 19):
            continue
        if not is_valid_luhn(digits):
            continue
        yield DetectionResult(
            label=LABEL,
            text=raw,
            start=m.start(),
            end=m.end(),
            risk_level=RiskLevel.HIGH,
            confidence=1.0,
            evidence=["pattern:card", "checksum:luhn_valid"],
            legal_basis=LEGAL_BASIS,
            extra={
                "digits": digits,
                "length": len(digits),
                "category": CATEGORY,
            },
        )
