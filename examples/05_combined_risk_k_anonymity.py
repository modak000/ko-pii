"""05. 결합 위험도 + k-익명성.

「개인정보 비식별 조치 가이드라인」 (개인정보보호위원회) 직접 대응.
"""
from k_pii import Anonymizer, ProcessingMode, k_anonymity

# Case 1: 단일 문서의 결합 위험도
print("=== 결합 위험도 평가 ===")
texts = {
    "이름만": "회의 참석자: 홍길동",
    "이름+전화": "홍길동 010-1234-5678",
    "이름+전화+주소+이메일": "홍길동 010-1234-5678 서울 강남구 hong@x.com",
    "RRN 포함": "홍길동 880101-1234568",
    "RRN + 의료": "홍길동 880101-1234568 처방번호 202412010001",
}

for name, text in texts.items():
    result = Anonymizer(mode=ProcessingMode.AUDIT).process(text)
    cr = result.combined_risk
    print(f"  {name:30} → {cr.combined_risk.name}")
    print(f"    {cr.rationale[-1]}")

# Case 2: 데이터셋 단위 k-익명성
print("\n=== k-익명성 평가 ===")
# 가명화된 레코드 5건 — 같은 (직장, 도시) 그룹
records = [
    {"PERSON": "<PERSON_1>", "ADDRESS": "서울특별시", "PHONE": "<PHONE_1>"},
    {"PERSON": "<PERSON_2>", "ADDRESS": "서울특별시", "PHONE": "<PHONE_2>"},
    {"PERSON": "<PERSON_3>", "ADDRESS": "서울특별시", "PHONE": "<PHONE_3>"},
    {"PERSON": "<PERSON_4>", "ADDRESS": "경기도",     "PHONE": "<PHONE_4>"},
    {"PERSON": "<PERSON_5>", "ADDRESS": "경기도",     "PHONE": "<PHONE_5>"},
]
rpt = k_anonymity(records, quasi_keys=["ADDRESS"], threshold=3)
print(f"  k = {rpt.k}, group count = {rpt.group_count}")
print(f"  threshold 3 만족? {rpt.satisfies_threshold}")
for r in rpt.rationale:
    print(f"  · {r}")
