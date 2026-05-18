"""17. 현실 종합 공문서 데모 — 모든 PII 카테고리 혼합 단일 문서.

실제 공공기관의 *결재공문 + 민원답변 + 인사문서 + 의료 + 사건처리* 가 한 문서
안에 모두 들어있는 *극한 시나리오*. k-pii 가 전체를 어떻게 처리하는지 보여줌.
"""
from __future__ import annotations

from k_pii import Anonymizer, ProcessingMode


DOCUMENT = """[기획재정부 결재공문]
문서번호: 기재부-인사-2024-00123

수신자: 행정안전부 장관
참조: 김민수 과장 (010-1234-5678)

다음 사항을 통보합니다.

────── 신청인 정보 ──────
성명: 홍길동 (남자, 45세)
주민등록번호: 880101-1234568
연락처: 010-9876-5432, 팩스 02-555-1234
이메일: hong.gildong@gov.go.kr
주소: 서울특별시 종로구 세종대로 209 (우편번호 03187)
직장: 보건복지부 (사업자등록번호 120-81-47521)
계좌: 110-1234-567890 (국민은행)

────── 처방 정보 (의료) ──────
환자명: 박영수
주민번호: 950101-2345676
처방번호 202412010001
진단코드: E11.9 (당뇨)
약품코드 123456789

────── 차량/토지 ──────
차량번호 12가3456
필지고유번호 1111011600100010000

────── 법조 ──────
관련 사건: 2024가합12345 (민사 합의)
법무부 정혜진 검사 담당

────── 외국인 정보 ──────
외국인 (FRN): 850315-5345676
여권 M12345678

────── 결재 라인 ──────
기안자: 이수정 사무관 (사번 20231234)
검토자: 최지훈 과장
결재자: 강도현 국장

기획재정부 김민수 장관님 결재 바랍니다.

본 안건은 사건번호 2023고합567 과 연계된 사항으로,
민원번호 2024-민원-00123 로 접수된 청구에 대한 후속 처리입니다.
"""


def main() -> int:
    print("=" * 80)
    print("실제 한국 공공 문서 시나리오 — Before / After 비교")
    print("=" * 80)
    print()
    print("── ORIGINAL (PII 노출됨) ──")
    print(DOCUMENT)
    print()
    print("=" * 80)

    # 4가지 시나리오 비교 — 모드 × 전략
    print("\n══ 1) STRICT (MEDIUM+) + tokenize ══")
    print("    → LOW 위험도 (VEHICLE/POSTAL/PNU/EDI/DOC_ID) 는 *통과* (정책)")
    print()
    anon = Anonymizer(mode=ProcessingMode.STRICT, strategy="tokenize")
    result = anon.process(DOCUMENT)
    print(result.text)
    print(f"\n  결합 위험도: {result.combined_risk.combined_risk.name}")
    print(f"  by_action: {dict(result.summary['by_action'])}")
    print(f"  검출 카테고리: {list(result.summary['by_label'].keys())}")
    print()
    print("─" * 80)

    print("\n══ 2) PARANOID (LOW+) + redact (가장 안전) ══")
    print("    → 모든 PII 카테고리 차단, 한글 라벨로 마스킹")
    print()
    anon = Anonymizer(mode=ProcessingMode.PARANOID, strategy="redact")
    result = anon.process(DOCUMENT)
    print(result.text)
    print(f"\n  by_action: {dict(result.summary['by_action'])}")
    print()
    print("─" * 80)

    print("\n══ 3) PARANOID + partial (실무 표준 양식) ══")
    print("    → 부분 가명화: 홍OO, 880101-1******, 010-****-5678 등")
    print()
    anon = Anonymizer(mode=ProcessingMode.PARANOID, strategy="partial")
    result = anon.process(DOCUMENT)
    print(result.text)
    print()
    print("─" * 80)

    print("\n══ 4) PARANOID + tokenize + Vault (분석 + 복원 가능) ══\n")
    anon = Anonymizer(mode=ProcessingMode.PARANOID, strategy="tokenize")
    result = anon.process(DOCUMENT)
    print(result.text)
    print(f"\n  Vault 복원표:")
    for entry in result.vault.entries():
        print(f"    {entry.token:22} ← {entry.original}")
    print(f"\n  총 {len(result.vault)} 토큰 — 권한 있는 사용자가 vault 로 원본 복원 가능")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
