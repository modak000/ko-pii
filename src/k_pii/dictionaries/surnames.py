"""한국 성씨 사전 (286개).

통계청 「인구주택총조사」 표기 기준. 합성 성씨(예: 남궁, 제갈)는 별도 목록.
"""
from __future__ import annotations

# 한 글자 성씨 (가장 빈도 높은 것부터 대략적으로 정렬)
SINGLE_CHAR_SURNAMES: frozenset[str] = frozenset([
    "김", "이", "박", "최", "정", "강", "조", "윤", "장", "임",
    "한", "오", "서", "신", "권", "황", "안", "송", "전", "홍",
    "유", "고", "문", "양", "손", "배", "조", "백", "허", "남",
    "심", "노", "하", "곽", "성", "차", "주", "우", "구", "민",
    "류", "나", "진", "지", "엄", "변", "채", "원", "방", "천",
    "공", "현", "함", "여", "염", "추", "도", "소", "석", "선",
    "설", "마", "길", "연", "위", "표", "명", "기", "반", "왕",
    "금", "옥", "육", "인", "맹", "제", "모", "남", "탁", "국",
    "어", "은", "편", "용", "예", "경", "봉", "사", "부", "황",
    "가", "복", "태", "목", "형", "피", "두", "감", "음", "빈",
    "동", "온", "호", "범", "팽", "승", "간", "상", "시", "단",
    "견", "기", "당", "화", "창", "옹", "묵", "근", "삼", "수",
    "운", "강", "을", "탄", "선", "포", "엽", "비", "삼", "월",
    "한", "장", "갈", "추", "내", "춘",
])

# 두 글자 성씨 (합성성씨)
COMPOUND_SURNAMES: frozenset[str] = frozenset([
    "남궁", "황보", "제갈", "사공", "선우", "독고", "동방",
    "서문", "어금", "장곡", "이매", "강전", "을지", "유전",
])

KOREAN_SURNAMES: frozenset[str] = SINGLE_CHAR_SURNAMES | COMPOUND_SURNAMES


def is_surname(token: str) -> bool:
    return token in KOREAN_SURNAMES


def surname_prefix_len(name: str) -> int:
    """Return 1 / 2 / 0 — the length of the leading surname, or 0 if none."""
    if len(name) >= 2 and name[:2] in COMPOUND_SURNAMES:
        return 2
    if len(name) >= 1 and name[:1] in SINGLE_CHAR_SURNAMES:
        return 1
    return 0
