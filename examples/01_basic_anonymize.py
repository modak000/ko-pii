"""01. 기본 가명화 — 가장 간단한 사용.

한국 공공 문서 텍스트에서 PII 를 자동 검출해 토큰으로 치환.
"""
from k_pii import Anonymizer, ProcessingMode

text = """
[기획재정부 결재공문]

수신자: 행정안전부 장관
참조: 김민수 과장

신청인: 홍길동
주민등록번호: 880101-1234568
연락처: 010-1234-5678
이메일: hong@example.go.kr
주소: 서울특별시 종로구 세종대로 209
""".strip()

# 1) Anonymizer 생성 — 기본: STRICT 모드 + tokenize 전략
anon = Anonymizer(mode=ProcessingMode.STRICT, strategy="tokenize")

# 2) 처리
result = anon.process(text)

print("=== 가명화된 텍스트 ===")
print(result.text)
print()
print("=== 결합 위험도 ===")
print(f"  level: {result.combined_risk.combined_risk.name}")
for r in result.combined_risk.rationale:
    print(f"  · {r}")
print()
print("=== 검출 카테고리 ===")
for label, count in result.summary["by_label"].items():
    print(f"  {label}: {count}")
print()
print("=== Vault (가명화 토큰 ↔ 원본) ===")
for entry in result.vault.entries():
    print(f"  {entry.token} → {entry.original}  ({entry.label})")
