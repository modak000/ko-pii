"""KCD (한국표준질병사인분류) 코드 detection — 식의약 도메인.

형식 (ICD-10 / KCD-8 기준, 통계청 + KOICD):
- 알파벳 1자 + 숫자 2자 + (선택) ``.`` + 숫자 1~2자
- 범위: A00.0 ~ Z99.9
- 알파벳 O 와 I 는 사용 안 함 (0/1 혼동 방지)
- 약 14,400 여 개 코드

검출 정책:
- 단독 토큰 "I10" 만으로는 변수명·라벨 등과 충돌 위험 큼
- **"진단", "질병코드", "ICD", "KCD" 키워드** 또는
- **알파벳 + 숫자 + ``.`` + 숫자 조합 (소수점 포함)** 일 때 신뢰도 높음

코드 첫 글자 분류:
  A,B  감염성 질환
  C,D  신생물·혈액
  E    내분비·대사
  F    정신·행동
  G    신경계
  H    안·이비인후
  J    호흡기
  K    소화기
  L    피부
  M    근골격
  N    비뇨생식
  O    임신·출산  (KCD 코드에는 O 글자는 사용되나, 이는 본 분류임)
  P    주산기
  Q    선천기형
  R    증상·이상소견
  S,T  손상·중독
  V-Y  외인
  Z    보건서비스 접촉 요인
  U    임시 분류 (코로나 등)

법적 근거: 개인정보보호법 제23조 (민감정보 — 건강), 의료법 제22조 (진료기록).

위험도: HIGH (민감속성 — 건강).
"""
from __future__ import annotations

import re
from typing import Iterator

from k_pii.core.types import DetectionResult, RiskLevel

LABEL = "KCD"
LEGAL_BASIS = "개인정보보호법 제23조; 의료법 제22조"
CATEGORY = "민감정보(건강)"

# ICD-10/KCD: 첫 글자 알파벳 + 2자리 숫자 + 선택 .숫자
# 알파벳 전 범위 (A~Z) 사용 — I10 (고혈압), O00 (임신 합병증) 등 모두 유효
_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])"
    r"([A-Z])"
    r"(\d{2})"
    r"(?:\.(\d{1,2}))?"
    r"(?![A-Za-z0-9])"
)

_KEYWORDS = ("진단", "진단코드", "질병", "질병코드", "상병", "상병코드",
             "ICD", "KCD", "주상병", "부상병")


def _category_for(letter: str) -> str:
    return {
        "A": "infectious", "B": "infectious",
        "C": "neoplasm",   "D": "neoplasm_blood",
        "E": "endocrine",
        "F": "mental",
        "G": "neurological",
        "H": "eye_ear",
        "J": "respiratory",
        "K": "digestive",
        "L": "skin",
        "M": "musculoskeletal",
        "N": "genitourinary",
        "I": "circulatory",
        "O": "pregnancy",
        "P": "perinatal",
        "Q": "congenital",
        "R": "symptoms",
        "S": "injury", "T": "injury",
        "U": "provisional",
        "V": "external", "W": "external", "X": "external", "Y": "external",
        "Z": "health_service_contact",
    }.get(letter, "unknown")


def _has_keyword_before(text: str, start: int, window: int = 20) -> str | None:
    head = text[max(0, start - window): start]
    for kw in _KEYWORDS:
        if kw in head:
            return kw
    return None


def detect(text: str) -> Iterator[DetectionResult]:
    for m in _PATTERN.finditer(text):
        letter = m.group(1)
        digits = m.group(2)
        sub = m.group(3)
        has_decimal = sub is not None

        # 키워드 anchor 가 있거나 소수점 형태면 신뢰도 ↑
        kw = _has_keyword_before(text, m.start())
        if not kw and not has_decimal:
            # 평이한 "A00" 단독은 FP 위험 → 거부
            continue

        confidence = 0.95 if (kw and has_decimal) else (
            0.9 if has_decimal else 0.8
        )
        evidence = ["pattern:kcd", f"category:{_category_for(letter)}"]
        if kw:
            evidence.append(f"keyword:{kw}")
        if has_decimal:
            evidence.append("has_decimal:true")

        yield DetectionResult(
            label=LABEL,
            text=m.group(0),
            start=m.start(),
            end=m.end(),
            risk_level=RiskLevel.HIGH,
            confidence=confidence,
            evidence=evidence,
            legal_basis=LEGAL_BASIS,
            extra={
                "category": CATEGORY,
                "letter": letter,
                "main_digits": digits,
                "sub_digits": sub,
                "kcd_category": _category_for(letter),
            },
        )
