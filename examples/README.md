# k-pii 사용 예제

본 디렉토리의 모든 스크립트는 *실행 가능*. `pip install -e ".[dev]"` 후
바로 돌려 결과를 확인할 수 있습니다.

| 파일 | 주제 | 추가 deps |
|---|---|---|
| `01_basic_anonymize.py` | 기본 가명화 | — |
| `02_vault_reveal.py` | Vault 토큰 ↔ 원본 복원 | — |
| `03_processing_modes.py` | 5 모드 비교 (PARANOID~AUDIT) | — |
| `04_strategies_compared.py` | 6 처리 전략 비교 | — |
| `05_combined_risk_k_anonymity.py` | 결합 위험도 + k-익명성 | — |
| `06_file_inputs.py` | HWPX/DOCX/XLSX/CSV 입력 | `[file]` 선택 |
| `07_tabular_csv.py` | CSV 컬럼-단위 처리 | — |
| `08_batch_processing.py` | 디렉토리 일괄 처리 | — |
| `09_review_workflow.py` | 검토 큐 + 피드백 학습 | — |
| `10_html_report.py` | HTML 검토 리포트 | — |
| `11_audit_log.py` | 감사 로그 (제29조) | — |
| `12_encrypted_vault.py` | Vault AES-GCM 암호화 | `[security]` |
| `13_llm_safe_filter.py` | LLM 호출 전 PII 필터 | — |
| `14_hybrid_with_privacy_filter.py` | OpenAI Privacy Filter 연계 | `[ml]` |
| `15_presidio_integration.py` | Microsoft Presidio plugin | `[presidio]` |

## 실행

```bash
cd /path/to/k-pii
python examples/01_basic_anonymize.py
```

각 스크립트는 *self-contained* (외부 파일 없이 작동).
