"""13. LLM 호출 전 PII 필터 — 가장 핫한 use case.

한국 공문서를 ChatGPT/Claude/Gemini API 에 보내기 전 자동 가명화.
응답 후 원본으로 복원.

「개인정보보호법 제17조 (제3자 제공)」 위반 회피 — PII 가 외부 LLM 서버에
원본 그대로 전송되는 것을 방지.
"""
from k_pii import Anonymizer, ProcessingMode

# 사용자가 ChatGPT 에 보내려는 한국 공문서
user_input = """다음 민원 응대문을 요약해줘:

신청인 홍길동(880101-1234568)이 2024년 5월 1일 민원을 제출함.
연락처: 010-1234-5678, 주소: 서울특별시 종로구 세종대로 209.
민원 내용: 환경부의 대기질 측정 결과 공개 요청.
처리 담당자: 환경부 김민수 과장.
"""

# Step 1: 가명화 (PII → 토큰)
anon = Anonymizer(
    mode=ProcessingMode.PARANOID,  # 가장 엄격 — 의심도 차단
    strategy="tokenize",
)
result = anon.process(user_input)
safe_for_llm = result.text
vault = result.vault

print("=== LLM 에 전송 안전한 텍스트 ===")
print(safe_for_llm)
print(f"\n결합 위험도: {result.combined_risk.combined_risk.name}")
print(f"차단된 PII: {result.summary['by_action'].get('BLOCK', 0)} 건")

# Step 2: LLM 호출 (여기서는 시뮬레이션)
# llm_response = openai.chat.completions.create(messages=[{"role":"user","content":safe_for_llm}])
fake_llm_response = (
    "<PERSON_1> 님이 2024년 5월 1일 민원을 제출하셨습니다. "
    "연락처는 <PHONE_1>, 주소는 <ADDRESS_1> 이며, "
    "환경부 <PERSON_2> 과장이 담당입니다."
)
print(f"\n=== LLM 응답 (가명 그대로) ===")
print(fake_llm_response)

# Step 3: 원본 복원 (사용자에게는 진짜 이름·번호로)
def reveal_tokens(text: str, vault) -> str:
    import re
    pattern = re.compile(r"<([A-Z_]+)_\d+>")
    def repl(m):
        token = m.group(0)
        original = vault.reveal(token)
        return original if original else token
    return pattern.sub(repl, text)

restored = reveal_tokens(fake_llm_response, vault)
print(f"\n=== 사용자에게 보여줄 (원본 복원) ===")
print(restored)
