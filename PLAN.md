# Project: Offline Arabic-to-English Translation Framework

This document outlines the plan for building a robust, offline Arabic-to-English translation tool.

## 1. Project Overview
The goal is to create a Python-based wrapper that reads a CSV file containing Arabic text, translates it to English using a modern offline model (**NLLB-200**), and saves the results in a new CSV file.

### Key Requirements
- **Offline Capability:** The translation model must run locally without internet access (after initial download).
- **Modern Architecture:** Using **facebook/nllb-200-distilled-600M**. This model provides high-quality translations for both Modern Standard Arabic and dialects, fitting well within the memory of a modern laptop (600M parameters, ~2.4GB).
- **Robustness:** Handle malformed CSV rows and translation errors gracefully.
- **Hardware Flexibility:** Auto-detect GPU (CUDA) availability but default to CPU if not found.

---

## 2. Proposed Technical Stack
- **Language:** Python 3.x
- **Core Library:** `transformers` (Hugging Face) with `torch`.
- **Data Handling:** `pandas` for flexible column mapping and robust CSV writing.
- **Model:** `facebook/nllb-200-distilled-600M`.

---

## 3. System Design

### Input Configuration
The script will allow configuring:
- `ID_COLUMN`: The header name for the row ID.
- `TEXT_COLUMN`: The header name for the Arabic text.
- `FALLBACK_TEXT`: Default text for failures.

### Output CSV Format
| ID | Arabic Text | Translated Text | Status | Error |
|----|-------------|-----------------|--------|-------|
| 1  | مرحباً | Hello | SUCCESS | |
| 2  | [Empty] | [Bad input text] | ERROR | Missing input text |
| 3  | ... | [Translation failed] | ERROR | Model inference failed |

### Failure Modes & Status Text
| Failure Mode | Standard Text | Error Column Detail |
|--------------|---------------|---------------------|
| Missing/Empty Input | `[Bad input text]` | Missing input text in row |
| Non-String Input | `[Bad input text]` | Input is not a valid string |
| Model Inference Error | `[Translation failed]` | Model failed to process this row |
| Token Limit Exceeded | `[Text too long]` | Input exceeds model token limit |
| Unexpected System Error| `[System Error]` | Unexpected error: [Exception message] |

---

## 4. Implementation Steps

### Phase 1: Research & Prototype (Complete)
- [x] Initial research on modern models.
- [x] Setup Git repository.

### Phase 2: Core Development (Next)
- [ ] **Dependency Setup:** Create `requirements.txt` and install `torch`, `transformers`, `pandas`, `sentencepiece`.
- [ ] **Download Script:** `scripts/download_model.py` to pre-cache the NLLB-200 model locally.
- [ ] **Translation Core:** `translator.py` - A class to load the model and handle the `ar -> en` pipeline.
- [ ] **CLI Wrapper:** `main.py` - Handles CSV I/O, configuration, and the processing loop.

### Phase 3: Robustness & Testing
- [ ] **Batch Processing:** Optimize for 1M+ rows by processing in chunks to avoid memory overflow.
- [ ] **Checkpointing:** Implement a mechanism to save progress incrementally and resume after a crash/interruption.
- [ ] **Logging:** Add file-based logging to track long-running processes.
- [ ] Create a `tests/` directory with a "poisoned" CSV to verify error handling.

### Phase 4: Finalization
- [ ] Create a `README.md` with setup instructions.
- [ ] Finalize configuration defaults.
