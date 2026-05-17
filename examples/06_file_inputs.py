"""06. 파일 입력 — HWPX/DOCX/XLSX/CSV/TXT 자동 디스패치.

확장자에 따라 적절한 reader 가 자동으로 호출됨.
"""
import tempfile
import os

from k_pii import Anonymizer
from k_pii.io_ import read_text, read_records

# 합성 CSV 생성 (실제로는 사용자의 공문서 파일)
with tempfile.TemporaryDirectory() as d:
    csv_path = os.path.join(d, "users.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("성명,주민번호,연락처,메모\n")
        f.write("홍길동,880101-1234568,010-1234-5678,신청\n")
        f.write("김민수,950101-2345676,010-9999-8888,보호자\n")

    # 1) read_text — 평문 추출
    text = read_text(csv_path)
    print("=== 평문 추출 ===")
    print(text)

    # 2) read_records — 구조화된 행 추출
    records = read_records(csv_path)
    print(f"\n=== 레코드 ({len(records)}건) ===")
    for r in records:
        print(f"  {r}")

    # 3) 처리
    print("\n=== 평문 가명화 ===")
    result = Anonymizer().process(text)
    print(result.text)

    # 4) 표 단위 가명화 (컬럼-aware)
    from k_pii.tabular import anonymize_records
    anon_records, vault = anonymize_records(records, strategy="partial")
    print(f"\n=== 표 단위 부분 마스킹 ===")
    for r in anon_records:
        print(f"  {r}")
