"""02. Vault 저장 + 토큰 복원.

가명화 후 토큰만 외부 시스템에 전달 → 필요 시 권한 있는 사용자가 vault 로 복원.
"""
from k_pii import Anonymizer, ReversibleVault

# 처리
anon = Anonymizer()
result = anon.process("신청인 홍길동(880101-1234568) 연락처 010-1234-5678")
print("가명본:", result.text)

# Vault 저장
result.vault.save("/tmp/vault.json")
print(f"\nVault 저장됨: /tmp/vault.json ({len(result.vault)} 항목)")

# ── 별도 프로세스에서 ──
v2 = ReversibleVault.load("/tmp/vault.json")
print("\nVault 다시 로드 + 복원:")
for entry in v2.entries():
    revealed = v2.reveal(entry.token)
    print(f"  {entry.token} → {revealed} (label={entry.label}, risk={entry.risk_level})")
