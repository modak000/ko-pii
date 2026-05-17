"""12. Vault AES-256-GCM 암호화.

개인정보보호법 제29조 안전조치의무 직접 대응 — Vault 평문 저장 금지.
``pip install k-pii[security]`` 필요.
"""
import os
import tempfile

from k_pii import Anonymizer, ReversibleVault

try:
    from k_pii.vault.encrypted import (
        is_encrypted_file,
        load_encrypted,
        save_encrypted,
    )
except ImportError:
    print("이 예제는 cryptography 가 필요합니다: pip install k-pii[security]")
    raise SystemExit(0)

PASSWORD = os.environ.get("KPII_VAULT_PASSWORD", "demo-password-only")

with tempfile.TemporaryDirectory() as d:
    # 1) 가명화 + vault 생성
    anon = Anonymizer(strategy="tokenize", vault=ReversibleVault(salt="demo"))
    result = anon.process("홍길동 880101-1234568 010-1234-5678")
    print("가명화:", result.text)

    # 2) 암호화 저장
    enc_path = os.path.join(d, "vault.kvault")
    save_encrypted(result.vault, enc_path, password=PASSWORD)
    print(f"\n암호화 vault 저장: {enc_path}")
    print(f"  파일 크기: {os.path.getsize(enc_path)} bytes")
    print(f"  암호화 확인: is_encrypted_file = {is_encrypted_file(enc_path)}")

    # 3) 잘못된 비밀번호 → 실패
    try:
        load_encrypted(enc_path, "wrong-password")
    except ValueError as e:
        print(f"\n잘못된 비밀번호 → {type(e).__name__}: 정상 거부")

    # 4) 올바른 비밀번호 → 복호화 성공
    v2 = load_encrypted(enc_path, password=PASSWORD)
    print(f"\n복호화 성공:")
    for entry in v2.entries():
        print(f"  {entry.token} → {entry.original}")
