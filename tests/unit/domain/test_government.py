from k_pii.core.types import RiskLevel
from k_pii.domain.government import detect


def _d(text):
    return list(detect(text))


class TestDocIdPositive:
    def test_basic_doc_id(self):
        results = _d("문서번호: 기재부-인사-2024-00123")
        assert len(results) == 1
        r = results[0]
        assert r.label == "DOC_ID"
        assert r.text == "기재부-인사-2024-00123"
        assert r.risk_level == RiskLevel.LOW

    def test_six_digit_serial(self):
        assert len(_d("행안부-총무과-2025-000567")) == 1

    def test_in_paragraph(self):
        text = "본 안건은 기재부-인사-2024-00123 으로 등록됨."
        results = _d(text)
        assert len(results) == 1


class TestDocIdNegative:
    def test_only_year_serial(self):
        # Not enough structure
        assert _d("2024-00123") == []

    def test_missing_year(self):
        assert _d("기재부-인사-abc-00123") == []

    def test_extra_alphanum_after(self):
        # Boundary check: should not match if trailing alphanumeric
        assert _d("기재부-인사-2024-001234A") == []


class TestDocIdStructure:
    def test_legal_basis(self):
        r = _d("기재부-인사-2024-00123")[0]
        assert r.legal_basis == "개인정보보호법 제2조"
        assert r.extra["domain"] == "government"
