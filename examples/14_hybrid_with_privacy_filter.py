"""14. OpenAI Privacy Filter 와 hybrid 연계 (옵셔널 ML).

``pip install k-pii[ml]`` 필요. 첫 실행 시 모델 다운로드 ~3GB.
GPU 없이 CPU 추론도 가능 (느림).

k-pii (룰) + Privacy Filter (ML) = 자연어 PII 검출 정밀도 + recall 모두 ↑
"""
from k_pii import Anonymizer, ProcessingMode

try:
    from k_pii.integrations import get_privacy_filter_adapter
except ImportError:
    print("integrations 모듈 import 실패")
    raise SystemExit(1)

text = """
다음은 회의록 발췌입니다.

오늘 회의에는 김기덕 감독, 강혜정 배우, 이범수 선생이 참석하셨고,
880101-1234568 주민등록번호의 김민수 씨도 함께 자리했습니다.
연락처는 010-1234-5678 입니다.
""".strip()

# === k-pii 단독 ===
print("=== k-pii 단독 ===")
anon_solo = Anonymizer(mode=ProcessingMode.STRICT, strategy="redact")
result_solo = anon_solo.process(text)
print(result_solo.text)
print(f"검출: {result_solo.summary['by_label']}\n")

# === k-pii + Privacy Filter (hybrid) ===
print("=== k-pii + Privacy Filter (hybrid) ===")
try:
    pf = get_privacy_filter_adapter(device="cpu")
    anon_hybrid = Anonymizer(
        mode=ProcessingMode.STRICT,
        strategy="redact",
        secondary_detector=pf,
        merge_mode="union",  # 합산
    )
    result_hybrid = anon_hybrid.process(text)
    print(result_hybrid.text)
    print(f"검출: {result_hybrid.summary['by_label']}")
except ImportError as e:
    print(f"transformers/torch 미설치: pip install k-pii[ml]")
    print(f"  ({e})")
except Exception as e:
    print(f"Privacy Filter 모델 로드 실패 (네트워크 또는 디스크): {e}")

# === 비교 ===
# 자연어 인명 (김기덕·강혜정·이범수·김민수) 중 k-pii 단독에서 놓친 것을
# Privacy Filter 가 보강.
