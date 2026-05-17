"""04. 6 처리 전략 비교.

tokenize / redact / asterisk / hashed / partial / fpe — 각 전략의 출력 차이.
"""
from k_pii import Anonymizer, ProcessingMode

text = "홍길동 880101-1234568 010-1234-5678"

for strategy in ("tokenize", "redact", "asterisk", "hashed", "partial", "fpe"):
    anon = Anonymizer(mode=ProcessingMode.STRICT, strategy=strategy)
    result = anon.process(text)
    print(f"{strategy:10} → {result.text}")
