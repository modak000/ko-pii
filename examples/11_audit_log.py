"""11. 감사 로그 — 개인정보보호법 제29조 (안전조치의무) 직접 대응.

모든 vault.store / vault.reveal 호출 추적 → JSONL 로 영구 보존.
"""
import os
import tempfile

from k_pii import Anonymizer, ReversibleVault
from k_pii.vault.audit import AuditLog, replay

with tempfile.TemporaryDirectory() as d:
    log_path = os.path.join(d, "audit.jsonl")

    # 1) AuditLog 활성화한 vault 사용
    with AuditLog(log_path, default_actor="alice@gov.kr") as log:
        vault = ReversibleVault(salt="audit-demo", audit_log=log)
        anon = Anonymizer(vault=vault, strategy="tokenize")
        result = anon.process("홍길동 880101-1234568 010-1234-5678")
        print("가명화:", result.text)

        # 권한 있는 사용자가 reveal 호출 — 컨텍스트 기록
        original = vault.reveal("<RRN_1>", context="BI 대시보드 추출")
        print(f"reveal: <RRN_1> → {original}")

        original = vault.reveal("<PHONE_1>", context="상담 처리")
        print(f"reveal: <PHONE_1> → {original}")

    # 2) 감사 로그 리플레이
    print(f"\n=== 감사 로그 (제29조 처리 이력) ===")
    for entry in replay(log_path):
        print(f"  [{entry['ts']}] {entry['action']:10} {entry.get('token', '-'):15} "
              f"by {entry['actor']:20} ctx={entry.get('context', '-')}")
