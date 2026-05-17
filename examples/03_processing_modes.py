"""03. 5 처리 모드 비교.

PARANOID / STRICT / BALANCED / PERMISSIVE / AUDIT — 각 모드의 차단 임계값 차이.
"""
from k_pii import Anonymizer, ProcessingMode

text = "주민번호 880101-1234567 입니다"   # 체크섬 fail → 후-2020 RRN, conf 0.7

for mode in ProcessingMode:
    anon = Anonymizer(mode=mode, strategy="redact")
    result = anon.process(text)
    by_action = result.summary["by_action"]
    print(f"{mode.name:11}: {result.text:40} | {dict(by_action)}")
