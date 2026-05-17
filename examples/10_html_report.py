"""10. HTML 검토 리포트 생성.

단일 정적 HTML — 원본 / 가명본 사이드 바이 사이드, 카테고리 색상 코딩,
인터랙티브 마킹 (사람 검토용).
"""
import tempfile
import os
import webbrowser

from k_pii import Anonymizer, ProcessingMode
from k_pii.reporting.html_report import generate_html_report

text = """[기획재정부 결재공문]

수신자: 행정안전부 장관
참조: 김민수 과장

신청인: 홍길동(880101-1234568)
연락처: 010-1234-5678
이메일: hong@example.go.kr
주소: 서울특별시 종로구 세종대로 209

본 안건과 관련하여 상기 신청인의 민원을 처리 검토 바랍니다.
"""

anon = Anonymizer(mode=ProcessingMode.STRICT, strategy="tokenize")
result = anon.process(text)

html = generate_html_report(text, result, document_id="공문-2024-00123",
                             enable_marking=True)

out_path = os.path.join(tempfile.gettempdir(), "kpii_report.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"HTML 리포트 생성: {out_path}")
print(f"  파일 크기: {len(html):,} bytes")
print(f"  결합 위험도: {result.combined_risk.combined_risk.name}")
print(f"  검출 카테고리: {list(result.summary['by_label'].keys())}")
print(f"\n  브라우저로 열어보세요: file://{out_path}")
