def test_config_values():
    """Verify that configuration constants are correctly loaded."""
    import config
    assert config.SRC_LANG == "arb_Arab"
    assert config.TGT_LANG == "eng_Latn"
    assert config.MAX_LENGTH == 512
    assert config.INFERENCE_BATCH_SIZE > 0

def test_failure_strings():
    """Verify that fallback error strings are defined."""
    import config
    assert "[Bad input text]" in config.ERR_BAD_INPUT
    assert "[Translation failed]" in config.ERR_TRANS_FAILED
