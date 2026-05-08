import os

import pytest

from src import config
from src.translator import ArabicTranslator


@pytest.fixture(scope="module")
def translator():
    if not os.path.exists(config.MODEL_PATH):
        pytest.skip("Model assets missing. Run scripts/download_model.py first.")
    return ArabicTranslator()


def test_hand_crafted_translations(translator):
    """
    Validate the model against human-verified semantic ground-truth.
    Uses keyword-based matching to ensure professional accuracy while allowing
    for model-specific linguistic variations.
    """
    # Format: (Arabic Input, [List of Mandatory Keywords/Phrases])
    ground_truth = [
        ("مرحبا بالعالم", ["world", "welcome"]),
        ("تقرير الميزانية السنوية", ["budget", "report"]),
        ("محضر اجتماع مجلس الإدارة", ["minutes", "board", "meeting"]),
        ("وثيقة رسمية سرية", ["official", "document", "secret"]),
        ("قرار وزاري رقم ١٢٣", ["decision", "123"]),
        ("وزارة العدل", ["ministry", "justice"]),
        ("المملكة العربية السعودية", ["saudi", "arabia"]),
    ]

    for arabic_text, keywords in ground_truth:
        result, status, error = translator.translate(arabic_text)

        assert status == "SUCCESS", f"Failed to translate: {arabic_text}"

        result_lower = result.lower()
        for kw in keywords:
            assert kw.lower() in result_lower, (
                f"Accuracy Failure: '{arabic_text}' translated to "
                f"'{result}', missing keyword '{kw}'"
            )
