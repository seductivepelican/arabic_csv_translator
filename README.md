# Arabic to English Offline Translator 🌍

[![Python tests](https://github.com/seanpor/arabic_csv_translator/actions/workflows/test.yml/badge.svg)](https://github.com/seanpor/arabic_csv_translator/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance, robust, and entirely offline framework for translating large-scale Arabic document metadata to English. Powered by Meta's **NLLB-200** model.

## Key Features
- **Batched Inference:** Optimized for multi-core CPUs/GPUs, processing up to 20,000 rows/hour.
- **Fault Tolerant:** Automatic state checkpointing allows resuming 1M+ row batches after any interruption.
- **Data Integrity:** Preserves original CSV structure and document IDs.
- **Containerized:** Docker support for instant, zero-config deployment.
- **Professional CLI:** Featuring `tqdm` progress tracking and formal logging.

---

## 🚀 Quick Start

### 1. Local Setup
```bash
# Create and activate environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download model assets (One-time, 2.4GB)
python scripts/download_model.py
```

### 2. Usage
```bash
python main.py --input data.csv --output results.csv
```

### 3. Docker (Instant Deployment)
Build and run the containerized translator:
```bash
docker build -t arabic-translator .
docker run -v $(pwd):/data arabic-translator --input /data/input.csv --output /data/output.csv
```

---

## 🛠 Configuration
Adjust settings in `config.py` to match your hardware and dataset:
- `INFERENCE_BATCH_SIZE`: Set to 8-16 for CPU, 32-64 for GPU.
- `CHECKPOINT_BATCH_SIZE`: Frequency of disk persistence.
- `ID_COLUMN` & `TEXT_COLUMN`: Map to your CSV headers.

---

## 📊 Performance Projections (CPU)
| Dataset Size | Estimated Time |
| :--- | :--- |
| 1,000 rows | 3 minutes |
| 10,000 rows | 30 minutes |
| 1,000,000 rows | 50 hours (approx. 2 days) |

*Note: Performance on GPU is typically 5-10x faster.*

---

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎓 Documentation
A detailed technical report is available in [technical_report.pdf](technical_report.pdf).
