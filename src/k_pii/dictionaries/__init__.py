"""사전 (Dictionaries) — 한국 공공 부문 도메인에 특화된 어휘 자원.

CLAUDE.md §12 에 따라 본 사전들은 *시드* 데이터다. 도메인 전문가(사용자)가
실무 데이터로 큐레이션·확장하는 것이 정확도의 핵심.
"""
from k_pii.dictionaries.surnames import KOREAN_SURNAMES, is_surname
from k_pii.dictionaries.titles import TITLES, TITLES_GOV, is_title
from k_pii.dictionaries.agencies import AGENCIES, is_agency
from k_pii.dictionaries.field_labels import FIELD_LABELS, is_field_label
from k_pii.dictionaries.common_words import COMMON_WORDS, is_common_word

__all__ = [
    "KOREAN_SURNAMES", "is_surname",
    "TITLES", "TITLES_GOV", "is_title",
    "AGENCIES", "is_agency",
    "FIELD_LABELS", "is_field_label",
    "COMMON_WORDS", "is_common_word",
]
