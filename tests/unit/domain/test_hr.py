from k_pii.core.types import RiskLevel
from k_pii.domain.hr import detect


def _d(text):
    return list(detect(text))


class TestEmployeeIdPositive:
    def test_sabeon_keyword(self):
        results = _d("사번: 20231234")
        assert len(results) == 1
        assert results[0].label == "EMPLOYEE_ID"
        assert results[0].text == "20231234"

    def test_other_keywords(self):
        assert len(_d("공무원번호 123456")) == 1
        assert len(_d("교번 789012")) == 1
        assert len(_d("직원번호: 456789")) == 1


class TestEmployeeIdNegative:
    def test_no_keyword_no_match(self):
        assert _d("20231234") == []

    def test_keyword_too_far(self):
        # 30 chars between keyword and number — outside window
        assert _d("사번 입력 이후 한참 뒤에 적혀있는 번호 12345678") == []


class TestEmployeeIdStructure:
    def test_legal_basis(self):
        r = _d("사번 20231234")[0]
        assert "국가공무원법" in r.legal_basis
        assert r.risk_level == RiskLevel.MEDIUM
