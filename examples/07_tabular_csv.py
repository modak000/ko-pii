"""07. CSV/Excel 컬럼-단위 가명화.

표 형식 데이터에서 PII 컬럼만 가명화. 원본 구조 보존 → 분석 호환성.
"""
from k_pii.tabular import anonymize_records, map_columns

# 사용자 데이터 (예: HR 데이터)
records = [
    {"성명": "홍길동", "주민번호": "880101-1234568", "부서": "기획팀", "연봉": 50000000},
    {"성명": "김민수", "주민번호": "950101-2345676", "부서": "개발팀", "연봉": 60000000},
    {"성명": "박영수", "주민번호": "770515-1234565", "부서": "기획팀", "연봉": 55000000},
]

# 헤더 → PII 라벨 자동 매핑
print("=== 컬럼 라벨 매핑 ===")
mapping = map_columns(records[0].keys())
for header, label in mapping.items():
    print(f"  {header:8} → {label}")

# 가명화 (tokenize 전략: 분석 호환)
out, vault = anonymize_records(records, strategy="tokenize")
print("\n=== 가명화 결과 ===")
for r in out:
    print(f"  {r}")

# 같은 사람 = 같은 토큰 (분석 호환성)
records2 = [
    {"성명": "홍길동", "주민번호": "880101-1234568", "방문일": "2024-12-01"},
]
out2, _ = anonymize_records(records2, vault=vault, strategy="tokenize")
print("\n=== 같은 vault 재사용 — 같은 토큰 ===")
print(f"  {out2[0]}")
print(f"  → 홍길동 → {vault.token_for('PERSON', '홍길동')} (이미 가명화된 토큰 재사용)")
