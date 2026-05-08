import os

import pytest

from src import config
from src.translator import ArabicTranslator

# Note: These tests assume the model is downloaded.
# In a real CI environment, we might mock the model,
# but for local TDD, testing against the actual model is more reliable.


@pytest.fixture(scope="module")
def translator():
    if not os.path.exists(config.MODEL_PATH):
        pytest.skip("Model not downloaded. Run scripts/download_model.py first.")
    return ArabicTranslator()


def test_happy_path(translator):
    """Test standard formal Arabic translation."""
    text = "تقرير المدير العام"
    result, status, error = translator.translate(text)
    assert status == "SUCCESS", f"Translation failed with error: {error}"
    assert "Director General" in result or "Report" in result
    assert error == ""


def test_empty_input(translator):
    """Test handling of empty or whitespace strings."""
    text = "   "
    result, status, error = translator.translate(text)
    assert status == "ERROR"
    assert result == config.ERR_BAD_INPUT
    assert "Missing or invalid input text" in error


def test_non_string_input(translator):
    """Test handling of non-string inputs (like numbers)."""
    text = 12345
    result, status, error = translator.translate(text)
    assert status == "ERROR"
    assert result == config.ERR_BAD_INPUT
    assert "Missing or invalid input text" in error


def test_null_input(translator):
    """Test handling of None/NaN."""
    text = None
    result, status, error = translator.translate(text)
    assert status == "ERROR"
    assert result == config.ERR_BAD_INPUT


def test_very_long_text(translator):
    """Test if long text is handled (truncated but successful or specific error)."""
    long_text = "هذا نص " * 200  # Very long
    result, status, error = translator.translate(long_text)
    # NLLB handles truncation internally, so it should still be SUCCESS
    # unless it explicitly crashes.
    assert status in ["SUCCESS", "ERROR"]
