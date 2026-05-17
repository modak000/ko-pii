"""09. 검토 큐 + 피드백 학습 워크플로우.

룰 기반의 한계를 보완 — 사람이 검토 마킹 → 사전 자동 후보 생성.
"""
import os
import tempfile

from k_pii import Anonymizer, ProcessingMode
from k_pii.review import ReviewQueue, Verdict, apply_feedback

with tempfile.TemporaryDirectory() as d:
    q_path = os.path.join(d, "review.jsonl")
    queue = ReviewQueue(q_path)

    # 1) PERMISSIVE 모드로 처리 → REVIEW 항목 발생
    text = "주민번호 880101-1234567 (후-2020 RRN 의심)"
    anon = Anonymizer(mode=ProcessingMode.PERMISSIVE)
    result = anon.process(text)

    # 2) REVIEW 항목을 큐에 추가
    items = queue.enqueue_review_records(result.review_items(), document="doc.txt")
    print(f"검토 큐에 추가된 항목: {len(items)}")
    for item in queue.pending():
        print(f"  [{item.id[:8]}] {item.label}: {item.text} (conf {item.confidence:.2f})")

    # 3) 사람 검토 시뮬레이션 — 일부 FP 마킹
    queue.mark(items[0].id, Verdict.OK, by="reviewer1", note="확실한 RRN")

    # 4) FP 사례 시뮬레이션
    fake_text = "사례 분석: 일반 단어 '검토'"
    anon2 = Anonymizer(mode=ProcessingMode.AUDIT)  # 모든 검출 ALLOW → 직접 큐에 넣음
    for d_ in anon2.process(fake_text).detections:
        queue.enqueue_detection(d_.detection, document="fake.txt")
    for it in queue.pending():
        if it.text == "검토":
            queue.mark(it.id, Verdict.FP, note="일반 단어")
            queue.mark(it.id, Verdict.FP, note="중복 확인")
            queue.mark(it.id, Verdict.FP, note="확정")

    # 5) 피드백 학습 → common_words 후보 생성
    patches_dir = os.path.join(d, "patches")
    summary = apply_feedback(q_path, patches_dir, min_repeat=1)
    print(f"\n피드백 학습 결과:")
    print(f"  OK: {summary.ok_count}, FP: {summary.fp_count}, FN: {summary.fn_count}")
    if summary.common_word_candidates:
        print(f"  common_words 후보: {summary.common_word_candidates}")

    # 6) 큐 통계
    stats = queue.stats()
    print(f"\n검토 큐 통계: {stats}")
