from services.gemini_service import evaluate_answer
from services.readiness_service import calculate_readiness


def test_readiness_formula():
    readiness = calculate_readiness(80, 60, 40, 100)
    assert readiness["score"] == 66.0


def test_gemini_fallback_is_useful(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    result = evaluate_answer("How did you design the API?", "I designed a Python API, tested it, and used metrics to improve performance.")
    assert 0 <= result["score"] <= 100
    assert result["feedback"]
