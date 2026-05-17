"""08. 디렉토리 일괄 처리 — multiprocessing 병렬.

대량 공문서 자동 가명화 워크플로우.
"""
import os
import tempfile

from k_pii.batch import process_paths
from k_pii.core.modes import ProcessingMode

with tempfile.TemporaryDirectory() as d:
    in_dir = os.path.join(d, "in")
    out_dir = os.path.join(d, "out")
    os.makedirs(in_dir)

    # 10개 합성 문서 생성
    for i in range(10):
        with open(os.path.join(in_dir, f"doc_{i:03d}.txt"), "w", encoding="utf-8") as f:
            f.write(f"신청인 사람{i}\n주민번호 88010{i:02d}-1234568\n연락처 010-1234-{i:04d}\n")

    # 일괄 처리 — 4 워커 병렬
    summary = process_paths(
        inputs=[in_dir],
        output_dir=out_dir,
        mode=ProcessingMode.STRICT,
        strategy="redact",
        workers=2,   # 데모용; 실제 운영은 CPU 코어 수만큼
        progress=False,
    )

    print(f"\n=== 배치 결과 ===")
    print(f"  총 {summary.total_files} 파일")
    print(f"  성공: {summary.succeeded}, 실패: {summary.failed}")
    print(f"  검출: {summary.total_detections}, 차단: {summary.total_blocked}")
    print(f"  소요: {summary.elapsed_s:.2f}초")

    # 출력 파일 확인
    print(f"\n=== 출력 샘플 (doc_001) ===")
    with open(os.path.join(out_dir, "doc_001.txt"), encoding="utf-8") as f:
        print(f.read())
