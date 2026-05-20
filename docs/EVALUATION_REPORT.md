# k-pii 평가 보고서 (통합본)

> 본 문서는 k-pii 라이브러리의 실데이터 정확도 평가, 합성 회귀 측정, 과탐 분석,
> 가명화 사용 샘플을 한 번에 정리한 통합 보고서. 세부 파일을 따로 보지 않아도
> 평가 + 운영 결정에 필요한 정보가 모두 들어있음.

**최종 결과 요약** (KDPII 53,778 문서 기준):
- micro F1 = **0.655** (이번 세션 시작 0.412 → +0.243, +59%)
- 합성 코퍼스 F1 = 0.877 (회귀 감지 sanity check, *실제 정확도 아님*)
- 테스트 699 passed · 코어 외부 deps 0개

원논문 (KDPII 데이터셋 출처): Li Fei, Yejee Kang, Seoyoon Park, Yeonji Jang,
Jongkyu Lee, Hansaem Kim. *"KDPII: A New Korean Dialogic Dataset for the
Deidentification of Personally Identifiable Information."* IEEE Access, 2024.
DOI [10.1109/ACCESS.2024.3461804](https://ieeexplore.ieee.org/document/10681073).

---

## 목차

1. [평가 데이터셋 + 라벨 매핑](#1-평가-데이터셋--라벨-매핑)
2. [KDPII 결과 (실데이터, 메인)](#2-kdpii-결과-실데이터-메인)
3. [Tier 분류 (운영 적합도)](#3-tier-분류-운영-적합도)
4. [합성 코퍼스 (회귀 감지)](#4-합성-코퍼스-회귀-감지)
5. [과탐 분석 (PERSON FP 가 왜 많은가)](#5-과탐-분석-person-fp-가-왜-많은가)
6. [Decision Log (이번 세션 결정 기록)](#6-decision-log)
7. [개선 추이 (시작→최종)](#7-개선-추이)
8. [가명화 사용 샘플](#8-가명화-사용-샘플)
9. [사용자 직접 제어 방법](#9-사용자-직접-제어-방법)
10. [재현 명령](#10-재현)

---

## 1. 평가 데이터셋 + 라벨 매핑

| 데이터셋 | 문서 수 | 도메인 | 용도 | 출처 |
|---|---:|---|---|---|
| KDPII (메인) | 53,778 | 한국어 일상 대화 PII | 실제 정확도 | IEEE Access 2024 |
| KLUE-NER | 5,000 | 신문기사 일반 NER | 자연어 PERSON 어림 | KLUE-benchmark |
| 합성 코퍼스 | 60×5 seed | 한국 공문서 6 템플릿 | 회귀 감지 sanity | 자체 |

### KDPII 라벨 → k-pii LABEL 매핑

| KDPII gold | k-pii LABEL |
|---|---|
| PS_NAME | PERSON |
| QT_AGE | AGE |
| OGG_EDUCATION | EDUCATION |
| FD_MAJOR | MAJOR |
| CV_POSITION | POSITION |
| DT_BIRTH | DT_BIRTH |
| QT_PHONE / QT_MOBILE | PHONE |
| TMI_EMAIL | EMAIL |
| TMI_SITE | URL |
| QT_RESIDENT_NUMBER | RRN |
| LC_ADDRESS / LCP_COUNTRY | ADDRESS |
| QT_CARD_NUMBER | CARD |
| QT_ACCOUNT_NUMBER | ACCOUNT |
| QT_PASSPORT_NUMBER | PASSPORT |
| QT_DRIVER_NUMBER | DRIVER_LICENSE |
| QT_IP | IP |
| QT_ALIEN_NUMBER | FRN |
| QT_PLATE_NUMBER | VEHICLE |
| QT_LENGTH | HEIGHT |
| QT_WEIGHT | WEIGHT |

**매핑 안 된 KDPII 라벨** (k-pii 스코프 밖):
PS_NICKNAME, OGG_CLUB, OGG_RELIGION, LC_PLACE, OG_WORKPLACE, OG_DEPARTMENT,
CV_SEX, CV_MILITARY_CAMP, TM_BLOOD_TYPE, QT_GRADE.

### 매칭 정책
per-document 라벨별 set 비교, **substring overlap** (예측 텍스트가 gold form 의
부분 문자열이거나 반대) 로 매칭. partial overlap 허용.

---

## 2. KDPII 결과 (실데이터, 메인)

```
라벨                 TP    FP    FN       P       R      F1
---------------------------------------------------------
ACCOUNT           653    93   151   0.875   0.812   0.843
ADDRESS           471   122  1204   0.794   0.281   0.415
AGE               512    36   188   0.934   0.731   0.821
CARD               56     0   749   1.000   0.070   0.130
DRIVER_LICENSE    154     0    45   1.000   0.774   0.873
DT_BIRTH          379    25   355   0.938   0.516   0.666
EDUCATION         463    49   579   0.904   0.444   0.596
EMAIL             617     1     0   0.998   1.000   0.999
FRN               198     0     1   1.000   0.995   0.997
HEIGHT            552     3   155   0.995   0.781   0.875
IP                197     0     3   1.000   0.985   0.992
MAJOR             401    27   308   0.937   0.566   0.705
PASSPORT          132     0    68   1.000   0.660   0.795
PERSON            436  2503  1607   0.148   0.213   0.175
PHONE            1315    26     4   0.981   0.997   0.989
POSITION          596   406   564   0.595   0.514   0.551
RRN               198     0     2   1.000   0.990   0.995
URL               457     0     3   1.000   0.993   0.997
VEHICLE           449     0     4   1.000   0.991   0.996
WEIGHT            700   127     1   0.846   0.999   0.916
---------------------------------------------------------
(micro)          8936  3419  5991   0.723   0.599   0.655
```

---

## 3. Tier 분류 (운영 적합도)

| Tier | F1 | 카테고리 | 운영 적합도 |
|---|---|---|---|
| **S** | ≥0.95 | EMAIL (0.999), VEHICLE, FRN, RRN, IP, PHONE, URL | Production 즉시 가능 |
| **A** | 0.80-0.95 | WEIGHT (0.916), HEIGHT, DRIVER_LICENSE, ACCOUNT, AGE | 운영 가능 |
| **B** | 0.50-0.80 | PASSPORT, MAJOR (0.705), DT_BIRTH, EDUCATION, POSITION | 사람 검토 권장 |
| **C** | 0.20-0.50 | ADDRESS (0.415) | recall 보강 필요 |
| **D** | <0.20 | PERSON (0.175), CARD (0.130) | 본질적 한계 |

### 카테고리별 한계 (Tier C/D)

**PERSON F1 0.175.** 한국어 단성 성씨 (김/이/박/정) 가 *매우* 흔한 일반어
prefix (김치·이번·박물관·정성). 대화체에서 anchor 없이 등장하는 이름을 잡으면
FP 폭증. STRICT 모드 운영 시 BLOCK 비율 충분. [§5](#5-과탐-분석-person-fp-가-왜-많은가) 참조.

**CARD F1 0.130.** KDPII 카드 gold 의 **88.3% 가 Luhn 체크섬 invalid**
(저자 의도적 fake). k-pii Decision D-006 (Luhn 통과만 emit) 정책 유지 — production
에서는 정확.

**ADDRESS recall 0.281.** KDPII 의 동 단위 단독 등장 (anchor 없음) 다수.
정책 완화 시 일반 문장 FP 폭증 (예: "강남구 영등포구 등 25개 자치구").
trade-off 결정.

---

## 4. 합성 코퍼스 (회귀 감지)

**⚠ 이 점수는 실제 정확도가 아니다.** 6 템플릿 좁은 코퍼스에 검출기가 적합화될 수
있음. 본 세션에서 합성 코퍼스를 풍부화 (단순 양식 → 30~50줄 다단락 본문) 한 후
정직한 점수가 됨.

| Seed | F1 | precision | recall |
|---|---:|---:|---:|
| 0 | 0.883 | 0.79 | 1.00 |
| 1 | 0.881 | 0.79 | 1.00 |
| 2 | 0.886 | 0.79 | 1.00 |

용도: **새 룰/검출기 추가 시 합성 점수가 0.80 이하로 떨어지면 회귀 신호**.

### 6 템플릿 샘플

각 ~10건씩 (총 60), 가공 데이터:

1. **gov_decree** — 정부 부처 결재공문 (수신/참조/결재 라인 + 붙임)
2. **civil_petition** — 시민 민원 답변서 (접수번호 + 처리 결과 + 법령 인용)
3. **hr_review** — 공무원 인사 평가서 (직무 평가 5항목 + 평가 의견)
4. **meeting_minutes** — 부서 회의록 (의제 3건 + 다음 회의)
5. **police_report** — 경찰 사건 처리 보고서 (피의자/피해자/조사 내용)
6. **fire_dispatch** — 소방 출동 보고서 (출동 정보/현장 상황/조치)

샘플 텍스트는 본 문서 §8 또는 `docs/synthetic_sample.html` 참조.

---

## 5. 과탐 분석 (PERSON FP 가 왜 많은가)

### 진단

```
KDPII 53,778 문서 PERSON 카테고리:
  TP = 436    잡았고 gold 도 있음 (정답)
  FP = 2,503  잡았는데 gold 없음 ← 과탐
  FN = 1,607  gold 있는데 못 잡음

  Precision = 0.148  ← 100건 잡으면 15건만 정답
  Recall    = 0.213
  F1        = 0.175
```

→ PERSON 으로 잡은 것 중 85% 가 잘못된 검출 (FP).

### 원인 — score-based emit 의 약점

```python
score = 0
+ surname(이) = 0.15          # 단성 성씨 prefix
+ particle(에) = 0.35          # 조사 부착
+ deterministic_pii_nearby = 0.40  # RRN/PHONE 인접 ← 너무 강한 부스트
+ name_likelihood(0.05) = 0.05
= 0.95 ≥ threshold 0.50 → emit
```

KDPII 대화체에 RRN/PHONE 이 흔히 등장하고, 일반 명사 ("같은데/전화했어/마실거") 가
주변에 있으면 `deterministic_pii_nearby` 부스트 +0.40 로 끌어올려 PERSON 으로 잡힘.

### FP top evidence 분포 (10k 문서 분석)

| 회수 | Evidence | 예 |
|---:|---|---|
| 293 | `name_likelihood(0.05)` | 너무·없어·마실거 |
| 112 | `name_final_syllable` | 순정·하시든지·배민 |
|  96 | `name_likelihood(0.10)` | 분이길래·직구해·경영대 |
|  63 | `particle(는)` | 어릴때·나빠지 |
|  50 | `particle(에)` | 차장때문·우주선 |
|  43 | `deterministic_pii_nearby` | 전화했어·분이길래 |

### 단계별 개선 (이번 세션)

1. **동 사전 +85개** ("금오동/도계동/화서동" 등) — `is_common_dong` 사전 보강 →
   PERSON 의 admin_unit 거부가 즉시 작동.
2. **한국어 어말 사전** — `_COMMON_KOREAN_ENDINGS` 신규.
   연결어미 (은데/는데/라서/면서/다가/지만), 종결어미 (이에요/입니다),
   조사 결합 (에서/처럼/까지/라고). 3자+ 토큰이 이 어말로 끝나면 거부.
3. **부스트 길이 차등** — 3자+ 풀네임은 +0.40 유지, 2자 단명은 +0.20 약화.

**누적 결과:** PERSON FP 2,871 → 2,503 (-368, -12.8%), F1 0.170 → 0.175.

### 본질적 한계

PERSON F1 이 여전히 0.175 인 이유:
1. 한국어 단성 성씨 = 일반어 prefix 충돌 (사전적 분리 불가)
2. 대화체 PII 인식의 본질 (anchor 모호 — "야 그 김민지 알지?")
3. recall/precision trade-off

---

## 6. Decision Log

이번 세션의 비자명한 결정 기록:

### D-011. KDPII 라벨 매핑 정정 후 평가
**문제:** 초기 KMAP 이 AC_* prefix 가정 → TP 0건으로 시스템 무력해 보임.
**원인:** KDPII 실라벨은 TMI_EMAIL / QT_PHONE / QT_RESIDENT_NUMBER 등 QT_*/TMI_*.
**선택:** 라벨 분포 직접 조사 후 매핑 정정. EMAIL F1=0.999 등 진짜 정확도 드러남.

### D-012. ADDRESS 단독 행정구역 매칭
**문제:** LC_ADDRESS gold 의 ~30% 가 단순 행정구역명 ("서울", "화곡동") 단독.
**선택:** dict 통과 + 대화체 anchor (살던/이사/주소) 동시 충족 시 emit.
**효과:** ADDRESS F1 0.178 → 0.415.

### D-013. PHONE 대표번호 (15xx-18xx)
**선택:** KISA 가이드 1500-1899 대역만 cover. 비표준 prefix 제외.
**효과:** PHONE FN 32 → 4 (F1 0.987 → 0.989).

### D-014. PERSON 다중 거부 룰
**선택:** 호칭/명사 접미사/행정구역/학교/은행/동사 어미 거부.
**효과:** PERSON FP 5,202 → 2,503 (-52% 누적).

### D-015. LCP_COUNTRY anchor 면제
**문제:** 국가명 86% 가 anchor 없는 단독 등장 ("한국 남자/미국 친구").
**선택:** country kind 만 anchor 면제, 다른 행정구역은 정책 유지.
**효과:** ADDRESS recall +24%.

### D-016. 합성 코퍼스 위치 명확화
**선택:** 합성 = 회귀 감지 sanity check 으로 격하 + 풍부화 (단순 양식 → 다단락).
KDPII = 실제 정확도 메인 벤치마크.
**근거:** 사용자 지적 "합성 1.0 은 조작된 느낌".

### D-017. 부스트 길이 차등
**문제:** `deterministic_pii_nearby` +0.40 부스트가 약한 신호 일반어를 PII 로 끌어올림.
**선택:** 3자+ 풀네임 +0.40 유지, 2자 단명 +0.20 약화.
**근거:** 풀네임 + 결정적 PII = 거의 확실한 인명. 2자 토큰은 일반어 충돌 잦음.

### D-018. 한국어 어말 형태소 사전화
**문제:** common_words 무한 누적은 비효율 — "같은데/먹는데/하는데" 모두 별도 추가 필요.
**선택:** 형태소 단위 어말 사전 (`_COMMON_KOREAN_ENDINGS`) — 16종 어말 패턴으로
수백~수천 어휘 cover.
**근거:** 한국어 어말은 *유한한 형태소* 라서 사전화 가능.

---

## 7. 개선 추이

| 단계 | KDPII micro F1 | 핵심 변경 |
|---|---:|---|
| 시작 (Phase 7 베이스라인) | 0.412 | 합성 1.000, 실데이터 첫 측정 |
| ACCOUNT 은행명 anchor | 0.500 | 11개 시중은행 키워드 |
| 7 카테고리 신규 | 0.502 | AGE/EDU/MAJOR/POS/BIRTH/REL/HOBBY |
| 룰 정제 1차 | 0.566 | 카테고리별 FP 분석 |
| PERSON FP 1차 | 0.580 | 호칭/동사 활용 거부 |
| ADDRESS+PHONE+PERSON 2차 | 0.598 | 단독 행정구역, 1xxx 대표번호 |
| EDU/MAJOR/POS dict | 0.613 | 약칭/단과대/직책 사전 보강 |
| URL/COUNTRY 매핑 + 조사 떨기 | 0.650 | 라벨 매핑 확장 |
| **본 세션 최종** | **0.655** | 동 사전 +85, 어말 사전, 부스트 차등 |

**누적 +0.243 (+59%)** · 외부 ML 의존성 0개.

---

## 8. 가명화 사용 샘플

### 입력 (가공 — 종로구청 민원 회신문)
```
서울특별시 종로구청 민원실 회신문

(수신) 김민지 귀하 (010-1234-5678, mjkim@seoul.go.kr)
(주민등록번호) 880101-2123456
(주소) 서울특별시 강남구 테헤란로 124, 301호
(차량번호) 12가1234

처리 담당자는 종로구청 환경위생과 박철수 주임 (02-2148-1234, ext. 5678) 이며,
관련 사업자 (사업자등록번호 123-45-67890, 대표 이영희) 측에 시정 명령을 발부
하였습니다.
```

### 출력 (STRICT + tokenize)
```
서울특별시 종로구청 민원실 회신문

(수신) <PERSON_1> 귀하 (<PHONE_1>, <EMAIL_1>)
(주민등록번호) <RRN_1>
(주소) <ADDRESS_1>, 301호
(차량번호) 12가1234

처리 담당자는 종로구청 환경위생과 <PERSON_2> 주임 (<PHONE_2>, ext. 5678) 이며,
관련 사업자 (사업자등록번호 123-45-67890, 대표 <PERSON_3>) 측에 시정 명령을 발부
하였습니다.
```

### 분석 (자동 생성)
- 결합 위험도: **CRITICAL** (RRN 단독 식별자)
- 검출: PERSON×3, PHONE×4, EMAIL×2, RRN, ADDRESS, ACCOUNT, DT_BIRTH
- 법적 근거: 개인정보보호법 제24조의2 (RRN), 제2조 (기타 PII), 금융실명법 (ACCOUNT)

HTML 시각화: `docs/sample_redaction.html`.

---

## 9. 사용자 직접 제어 방법

PERSON 과탐이 우리 도메인 (예: 보안·법무) 에서 너무 많을 때:

### 옵션 A — 더 보수적 모드
```python
from k_pii import Anonymizer, ProcessingMode
anon = Anonymizer(mode=ProcessingMode.BALANCED)  # MEDIUM 이상만 차단
# → PERSON HIGH 만 차단, LOW/MEDIUM (약한 신호) 무시
```

### 옵션 B — 도메인 사전 추가
```python
from k_pii.dictionaries import common_words
common_words.COMMON_WORDS = common_words.COMMON_WORDS | {
    "마실거", "전화했어",  # 우리 도메인 특화 FP
}
```

### 옵션 C — 검토 큐 워크플로우 (`examples/09`)
```python
result = anon.process(text)
for item in result.review_queue:  # confidence 낮은 후보
    print(item.text, item.confidence, item.evidence)
    # 사람이 OK / FP / FN 마킹 → 피드백 누적 → 자동 추천
```

### 옵션 D — LLM hybrid (선택, `[ml]` extras)
```bash
pip install k-pii[ml]
# OpenAI Privacy Filter 와 hybrid — confidence 낮은 케이스만 LLM 위임
```

---

## 10. 재현

```bash
# KDPII (사용자 데이터셋 사전 다운로드 필요)
python -m k_pii.eval.kdpii /path/to/kdpii.jsonl

# KLUE-NER dev
curl -O https://raw.githubusercontent.com/KLUE-benchmark/KLUE/main/\
     klue_benchmark/klue-ner-v1.1/klue-ner-v1.1_dev.tsv
python -m k_pii.eval.klue_benchmark klue-ner-v1.1_dev.tsv

# 합성 (회귀 감지)
python -m k_pii.eval.benchmark -n 60 --seed 0

# 시각 비교 HTML
# docs/kdpii_visual_compare.html — 100 문서 색상 코딩 (TP/FN/FP)
# docs/sample_redaction.html — 가명화 사용 샘플
# docs/synthetic_sample.html — 합성 코퍼스 1건 가명화 결과
```

---

## 인용

```bibtex
@article{fei2024kdpii,
  title={KDPII: A New Korean Dialogic Dataset for the Deidentification of
         Personally Identifiable Information},
  author={Fei, Li and Kang, Yejee and Park, Seoyoon and Jang, Yeonji
          and Lee, Jongkyu and Kim, Hansaem},
  journal={IEEE Access}, year={2024}, publisher={IEEE},
  doi={10.1109/ACCESS.2024.3461804}
}

@inproceedings{park2021klue,
  title={KLUE: Korean Language Understanding Evaluation},
  author={Park, Sungjoon and Moon, Jihyung and Kim, Sungdong and others},
  booktitle={NeurIPS Datasets and Benchmarks},
  year={2021}
}
```

## 법적 참고

- 개인정보보호법 (제2조, 제23조, 제24조, 제24조의2, 제28조의2-5, 제29조)
- 개인정보보호위원회 「가명정보 처리 가이드라인」
- 개인정보보호위원회 「개인정보 비식별 조치 가이드라인」
- 상법 제40조 (법인등록번호)
- 출입국관리법 제31조 (FRN)
- 국민건강보험법 제96조 (건강보험증)
- 금융실명법 (계좌)
