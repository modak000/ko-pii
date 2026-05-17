# Changelog

본 프로젝트는 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)
형식 + [Semantic Versioning](https://semver.org/lang/ko/) 을 따른다.

## [Unreleased]

## [1.0.0] - 2026-05-15

첫 정식 릴리스. 한국 공공 부문 PII 검출·가명화 도구로 production-ready 수준
도달. 외부 ML 없이 룰만으로 합성 공문서 F1=1.000, KLUE-NER (한국 인명만)
F1=0.331 달성.

### Added — Phase 11: OpenAI Privacy Filter 어댑터 (옵셔널 ML 통합)
- `integrations/` 모듈 — SecondaryDetector 프로토콜 + 어댑터들
- OpenAI Privacy Filter 어댑터 (Apache-2.0, 1.5B params, 다국어 PII)
- Hybrid Anonymizer — 4가지 병합 모드 (union/intersection/cross_validation/enrich_primary)
- `[ml]` extras — `transformers>=4.40`, `torch>=2.0` (옵셔널)

### Added — Phase 10: 솔루션 인프라
- HWP 5.x (OLE) + PDF 입력 — `[file]` extras (`olefile`, `pypdf`)
- 표 컬럼-단위 처리 (`tabular.py`) — CSV/XLSX 헤더 자동 매핑 (80+ 헤더)
- Vault 암호화 (AES-256-GCM + PBKDF2 480k iter) — `[security]` extras
- 감사 로그 (JSONL, 모든 reveal 추적) — 보호법 제29조 직접 대응
- 배치/병렬 처리 (multiprocessing) — CLI `--batch --workers N`
- 검토 큐 + 피드백 학습 (`review/`) — 사람-시스템 협업
- HTML 검토 리포트 (단일 정적 파일)
- 한자 → 한글 변환 + Revised Romanization

### Added — Phase 9: 부분 마스킹 + FPE + 식의약·법조 도메인
- `modes/partial.py` — 부분 마스킹 (홍OO, 880101-1******, 010-****-5678)
- `modes/fpe.py` — 형식 보존 가명화 (RRN 체크섬 자동 재계산)
- 신규 PII: KCD (질병코드), EDI_DRUG, COURT_CASE (법원 사건번호)

### Added — Phase 8: 결합 위험도 + k-익명성
- `analytics/combined_risk.py` — 식별자/준식별자/민감속성 4분류 + 조합 평가
- `analytics/k_anonymity.py` — k-익명성 평가 + 일반화 제안
- 신규 PII: PNU (필지고유번호)

### Added — Phase 7: 평가 + 문서화
- 합성 공문서 생성기 (6 템플릿, Faker 불사용)
- Precision/Recall/F1 메트릭 + 벤치마크 CLI
- KLUE-NER 외부 평가 (한국어 자연어 NER) + Korean-only 모드
- `docs/` — legal_mapping, risk_levels, coverage, real_data_evaluation

### Added — Phase 6: 통합 API + 정책 + 리포팅 + CLI
- `Anonymizer` 통합 클래스
- `ProcessingMode` (PARANOID/STRICT/BALANCED/PERMISSIVE/AUDIT)
- `legal/mapping.py` — 카테고리 ↔ 법조항 단일 매핑
- `reporting/{summary,certificate}.py` — 감사 증명서
- `k-pii` CLI 엔트리포인트

### Added — Phase 5: Vault + 처리 모드
- `vault/reversible.py` — 가역 가명화 (JSON schema v1, salted SHA-256)
- 6 처리 전략: tokenize / redact / asterisk / hashed / partial / fpe
- `generalization/` — 연령·날짜·주소·직업 일반화

### Added — Phase 4: 도메인 특화 룰
- `domain/government.py` — DOC_ID
- `domain/civil_petition.py` — PETITION_ID
- `domain/hr.py` — EMPLOYEE_ID

### Added — Phase 3: 컨텍스트 기반 이름 탐지
- 한국 성씨 사전 (286개)
- 직책 사전 (일반직 + 경찰 11계급, 소방 11계급, 군 19계급, 검사·법관·외무)
- 부처·청·위원회 사전 (정부조직법 19부6처18청6위원회 + 약칭)
- 행정구역 사전 (17 광역 + 226 기초자치단체)
- 한국어 조사 처리 + 누적 사전 (NameDictionary)
- 컨텍스트 점수 시스템 + 점수 보강 룰 (음절 통계, co-occurrence 등)

### Added — Phase 2: 비검증 PII (정규식 + 컨텍스트)
- PHONE (국제 +82 포함), EMAIL, POSTAL_CODE, IP (v4+v6),
  VEHICLE, URL, ADDRESS (도로명+지번), ACCOUNT, FAX

### Added — Phase 1: 결정적 PII (체크섬)
- RRN (주민등록번호) + 후-2020 무작위화 대응
- FRN (외국인등록번호)
- BUSINESS_REG, CORP_REG (체크섬)
- DRIVER_LICENSE, PASSPORT
- CARD (Luhn)
- MEDICAL_INSURANCE

[Unreleased]: https://github.com/modak000/k-pii/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/modak000/k-pii/releases/tag/v1.0.0
