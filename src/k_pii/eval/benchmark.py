"""Benchmark runner — ``python -m k_pii.eval.benchmark`` 로 실행.

CLI 실행 시 합성 코퍼스 50건 생성 → ``detect_all`` 로 예측 → 라벨별 P/R/F1
요약을 stdout 에 출력한다.
"""
from __future__ import annotations

import argparse

from k_pii.detect import detect_all
from k_pii.eval.metrics import format_report, score_corpus
from k_pii.eval.synth import generate_corpus


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="k-pii-benchmark",
        description="합성 공문서 코퍼스에서 k-pii 검출 정확도 평가",
    )
    p.add_argument("-n", "--num-docs", type=int, default=50)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--mode", choices=["partial", "strict"], default="partial")
    args = p.parse_args(argv)

    corpus = generate_corpus(args.num_docs, seed=args.seed)
    report = score_corpus(corpus, detect_all, mode=args.mode)
    print(format_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
