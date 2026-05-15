"""컨텍스트 분석 — 점수 기반 이름 탐지 및 누적 사전."""
from k_pii.context.particles import (
    PARTICLES,
    strip_trailing_particle,
    starts_with_particle,
)
from k_pii.context.name_dictionary import NameDictionary, NameRecord
from k_pii.context.context_rules import (
    NameCandidate,
    score_candidate,
    Score,
)

__all__ = [
    "PARTICLES",
    "strip_trailing_particle",
    "starts_with_particle",
    "NameDictionary",
    "NameRecord",
    "NameCandidate",
    "score_candidate",
    "Score",
]
