"""부처/기관 × 직급 조합 사전 — 가짜 직책 매칭 거부용.

특정직 (경찰·소방·군·검사·법관·외무) 은 *특정 기관에만* 존재하므로 강한 검증.
일반직 (장관·차관·실장·국장·과장 등) 은 모든 중앙 부처에 공통.

용도:
- "환경부 치안총감" → 무효 (치안총감은 경찰청)
- "기획재정부 사무관" → 유효
- "보건복지부 소방경" → 무효 (소방청 직급)
- "외교부 대사" → 유효
- "법무부 검사" → 유효 (검찰청 직급이지만 법무부 산하)

데이터 출처:
- 정부조직법 + 각 부처 직제규정
- 인사혁신처 「공무원 임용령」 별표
- 위키백과 「대한민국의 공무원」, 각 부처 항목
"""
from __future__ import annotations


# 모든 중앙 부처에 공통적인 일반직 직급·직위
_COMMON_GENERAL_TITLES: frozenset[str] = frozenset({
    # 정무직
    "장관", "차관", "차관보", "실장", "본부장", "단장",
    # 1~9급 직급
    "관리관", "이사관", "정이사관", "부이사관",
    "서기관", "행정서기관", "기술서기관",
    "사무관", "행정사무관", "기술사무관",
    "주사", "행정주사", "기술주사",
    "주사보", "행정주사보",
    "서기", "행정서기",
    "서기보", "행정서기보",
    # 보직
    "국장", "과장", "팀장", "계장", "주무관", "전문관",
    "감사관", "조사관", "심사관", "심의관", "조정관",
    "기획관", "정책관", "운영관",
    "비서관", "보좌관", "행정관",
    "연구관", "연구위원",
})


# 기관 → 그 기관에서만 사용 가능한 *특정직* 직급 집합
_SPECIALIZED_TITLES: dict[str, frozenset[str]] = {
    # 경찰청 (행정안전부 외청)
    "경찰청": frozenset({
        "치안총감", "치안정감", "치안감", "경무관", "총경",
        "경정", "경감", "경위", "경사", "경장", "순경",
        "경찰청장", "지방경찰청장", "경찰서장",
        "수사관", "형사", "교통경찰",
    }),
    # 소방청 (행정안전부 외청)
    "소방청": frozenset({
        "소방총감", "소방정감", "소방감", "소방준감", "소방정",
        "소방령", "소방경", "소방위", "소방장", "소방교", "소방사",
        "소방청장", "소방서장", "소방대장",
    }),
    # 검찰청 (법무부 산하)
    "검찰청": frozenset({
        "검찰총장", "고검장", "지검장", "차장검사",
        "부장검사", "부부장검사", "평검사", "검사",
        "고등검사장", "지방검사장",
    }),
    "공소청": frozenset({"공소청장", "검사"}),       # 2026 신설
    "중수청": frozenset({"중수청장", "수사관"}),       # 2026 신설
    # 법원
    "대법원": frozenset({"대법원장", "대법관"}),
    "고등법원": frozenset({"고등법원장", "판사", "부장판사", "수석부장판사"}),
    "지방법원": frozenset({"지방법원장", "판사", "부장판사"}),
    "헌법재판소": frozenset({"헌법재판소장", "헌법재판관"}),
    # 외교부 (대사·영사 등은 외무공무원)
    "외교부": frozenset({
        "특명전권대사", "대사", "공사", "총영사", "영사", "부영사",
        "참사관", "공사참사관",
        "1등서기관", "2등서기관", "3등서기관",
        "외무서기관", "외무사무관", "외무주사",
    }),
    # 국방부·합참 (군인 계급)
    "국방부": frozenset({
        "원수", "대장", "중장", "소장", "준장",
        "대령", "중령", "소령",
        "대위", "중위", "소위", "준위",
        "원사", "상사", "중사", "하사",
        "참모총장", "합참의장",
    }),
    # 병무청 (군 관련)
    "병무청": frozenset({"병무청장"}),
    # 우정사업본부 (과기정통부 산하)
    "우정사업본부": frozenset({
        "우정사업본부장", "우정사업관리관",
        "우정이사관", "우정부이사관", "우정서기관", "우정사무관",
        "우정주사", "우정주사보", "우정서기", "우정서기보",
        "집배원",
    }),
}


# 부 → 외청 매핑 (직급 검증에서 fall-through 용)
_MINISTRY_TO_AGENCIES: dict[str, frozenset[str]] = {
    "기획재정부": frozenset({"국세청", "관세청", "조달청", "통계청"}),
    "과학기술정보통신부": frozenset({"우주항공청", "우정사업본부"}),
    "외교부": frozenset({"재외동포청"}),
    "법무부": frozenset({"검찰청", "공소청", "중수청"}),
    "국방부": frozenset({"병무청", "방위사업청"}),
    "행정안전부": frozenset({"경찰청", "소방청"}),
    "농림축산식품부": frozenset({"농촌진흥청", "산림청"}),
    "산업통상자원부": frozenset({"특허청"}),
    "환경부": frozenset({"기상청"}),
    "보건복지부": frozenset({"질병관리청", "식품의약품안전처"}),
    "국토교통부": frozenset({"행정중심복합도시건설청", "새만금개발청"}),
    "해양수산부": frozenset({"해양경찰청"}),
    "문화체육관광부": frozenset({"문화재청", "국가유산청"}),
}


def valid_titles_for(agency: str) -> frozenset[str]:
    """주어진 기관에서 유효한 직급·직위 집합 반환.

    공통 일반직 + 해당 기관·산하 외청의 특정직 모두 포함.
    """
    valid = set(_COMMON_GENERAL_TITLES)
    # 직접 매핑
    if agency in _SPECIALIZED_TITLES:
        valid |= _SPECIALIZED_TITLES[agency]
    # 부 → 산하 외청 직급도 인정
    if agency in _MINISTRY_TO_AGENCIES:
        for child_agency in _MINISTRY_TO_AGENCIES[agency]:
            if child_agency in _SPECIALIZED_TITLES:
                valid |= _SPECIALIZED_TITLES[child_agency]
    return frozenset(valid)


def is_valid_agency_title(agency: str, title: str) -> bool:
    """``(기관, 직책)`` 조합이 가능한지 검증.

    >>> is_valid_agency_title("기획재정부", "사무관")
    True
    >>> is_valid_agency_title("환경부", "치안총감")
    False
    >>> is_valid_agency_title("행정안전부", "경찰청장")  # 산하 외청
    True
    """
    if not agency or not title:
        return False
    return title in valid_titles_for(agency)


def specialized_agencies_for(title: str) -> list[str]:
    """주어진 직책이 *유효한 기관* 들의 목록 (반대 매핑).

    >>> specialized_agencies_for("치안총감")
    ['경찰청']
    >>> specialized_agencies_for("대장")
    ['국방부']
    """
    out = []
    for agency, titles in _SPECIALIZED_TITLES.items():
        if title in titles:
            out.append(agency)
    return out
