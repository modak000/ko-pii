"""15. Microsoft Presidio plugin — k-pii 를 Presidio 의 Korean recognizer 로 등록.

``pip install k-pii[presidio]`` 필요.

Presidio 사용자가 한국 공공 PII 검출을 한 줄로 추가할 수 있게 함.
"""
try:
    from presidio_analyzer import AnalyzerEngine
    from k_pii.integrations.presidio_plugin import KPiiRecognizer
except ImportError:
    print("이 예제는 Presidio 가 필요합니다: pip install k-pii[presidio]")
    raise SystemExit(0)

# Presidio Analyzer 초기화 + k-pii recognizer 등록
analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(KPiiRecognizer())

# Presidio 가 한국 PII 도 인식
text = "홍길동(880101-1234568)의 연락처: 010-1234-5678"
results = analyzer.analyze(text=text, language="ko")

print("=== Presidio + k-pii 인식 결과 ===")
for r in results:
    print(f"  {r.entity_type:20} [{r.start}:{r.end}] '{text[r.start:r.end]}' "
          f"(score {r.score:.2f})")
