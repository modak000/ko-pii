from k_pii.core.types import RiskLevel
from k_pii.patterns.kcd import detect


def _d(text):
    return list(detect(text))


class TestKcdPositive:
    def test_basic_with_decimal(self):
        r = _d("E11.9 당뇨병")[0]
        assert r.label == "KCD"
        assert r.text == "E11.9"
        assert r.risk_level == RiskLevel.HIGH
        assert r.extra["letter"] == "E"
        assert r.extra["main_digits"] == "11"
        assert r.extra["sub_digits"] == "9"
        assert r.extra["kcd_category"] == "endocrine"

    def test_with_keyword_no_decimal(self):
        r = _d("진단코드 I10 고혈압")[0]
        assert r.text == "I10"
        assert r.extra["kcd_category"] == "circulatory"

    def test_pregnancy_o_code(self):
        # O 글자도 KCD 에서 사용 (임신·출산)
        r = _d("진단 O80.0 정상분만")[0]
        assert r.extra["kcd_category"] == "pregnancy"

    def test_keyword_and_decimal(self):
        r = _d("주상병: J20.9")[0]
        assert r.confidence == 0.95
        assert r.extra["kcd_category"] == "respiratory"

    def test_kcd_keyword(self):
        r = _d("KCD 코드: A00.0")[0]
        assert r.extra["kcd_category"] == "infectious"


class TestKcdNegative:
    def test_no_keyword_no_decimal_rejected(self):
        # "A00" 단독은 키워드 없으면 FP 위험 → 거부
        assert _d("A00 이라는 단어") == []

    def test_invalid_length(self):
        assert _d("진단 X9.9") == []  # 1자리 main digit


class TestKcdStructure:
    def test_legal_basis_sensitive(self):
        r = _d("진단코드 K29.7")[0]
        assert "제23조" in r.legal_basis
        assert r.extra["category"] == "민감정보(건강)"
