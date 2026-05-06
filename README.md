# Arabic to English Offline Translator

This project provides a robust, offline framework for translating Arabic text in CSV files to English using the NLLB-200 model.

## Setup Instructions

### 1. Install Dependencies
Ensure you have Python 3.8+ installed. Then run:
```bash
pip install -r requirements.txt
```

### 2. Download the Model (Online Step)
You must download the model once while connected to the internet. This will cache the ~2.4GB model in the `models/` directory.
```bash
python scripts/download_model.py
```

### 3. Usage (Offline)
Once the model is downloaded, you can run the translator entirely offline.

```bash
python main.py --input your_file.csv --output translated_file.csv
```

### 4. Robustness for Large Batches (1M+ Rows)
- **Checkpointing:** The script automatically saves progress every 32 rows (configurable in `config.py`). If the process crashes or is interrupted, simply run the same command again. It will detect the `.checkpoint` file and resume from where it left off.
- **Memory:** For very large files, ensure your laptop has enough RAM to load the CSV (a 1M row CSV typically needs 1-4GB of RAM depending on text length).
- **GPU/CPU:** It will automatically use a GPU if found, which is recommended for 1M+ rows to finish overnight. On a CPU, a million rows may take several days.

## Configuration
You can adjust column names and error messages in `config.py`.

### Default Failure Modes:
- **`[Bad input text]`**: Triggered if the input row is empty or not a string.
- **`[Translation failed]`**: Triggered if the model fails to process the row.
- **`[System Error]`**: Triggered for low-level issues (e.g., GPU Out of Memory).

The output CSV will include the original data plus three new columns:
1. `english_translation`: The result or the failure string.
2. `translation_status`: `SUCCESS` or `ERROR`.
3. `translation_error`: A detailed description of the error (if any).
