# Translation Configuration
ID_COLUMN = "id"
TEXT_COLUMN = "arabic_text"
TRANSLATED_COLUMN = "english_translation"
STATUS_COLUMN = "translation_status"
ERROR_COLUMN = "translation_error"

# Fallback Strings
ERR_BAD_INPUT = "[Bad input text]"
ERR_TRANS_FAILED = "[Translation failed]"
ERR_TEXT_TOO_LONG = "[Text too long]"
ERR_SYSTEM = "[System Error]"

# Model Configuration
MODEL_PATH = "./models/nllb-200-600M"
SRC_LANG = "arb_Arab"  # Modern Standard Arabic
TGT_LANG = "eng_Latn"  # English
MAX_LENGTH = 512       # NLLB default max length

# Processing Configuration
CHECKPOINT_BATCH_SIZE = 100  # Save progress every X rows
INFERENCE_BATCH_SIZE = 8     # Number of sentences to translate at once (Batched Inference)
CHECKPOINT_SUFFIX = ".checkpoint"
