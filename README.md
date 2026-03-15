# 🏠 AI Detailed Diagnostic Report (DDR) Generator

An AI-powered pipeline that automatically generates **Detailed Diagnostic Reports (DDR)** for property inspections by combining vision LLMs, deterministic reasoning, and a hallucination evaluation layer.

---

## 🧠 How It Works

The system follows a **Reliability-First Hybrid AI Architecture** — structured evidence is extracted first, then reasoning and report generation are performed on top of it.

| Stage | Description |
|-------|-------------|
| **1. Input** | Accepts two PDFs: an Inspection Report and a Thermal Imaging Report |
| **2. PDF → Images** | Each page is converted to high-resolution images via `pdftoppm` |
| **3. Vision LLM Extraction** | Multimodal LLM extracts structured JSON: property info, area observations, thermal readings |
| **4. Evidence Merge** | Inspection + thermal evidence aligned by location, surface context, and keyword similarity |
| **5. Severity Scoring** | Deterministic layer assigns `severity_level` (Low/Medium/High) and `confidence_score` (0–1) |
| **6. DDR Generation** | Guardrailed LLM generates a client-ready report using only structured evidence |
| **7. Safety Evaluator** | Second LLM validates the DDR for hallucinations, missing data, and conflicts |

---

## 🚀 Pipeline Architecture
```
Inspection PDF + Thermal PDF
        ↓
PDF → Page Images (pdftoppm)
        ↓
Vision LLM Structured Extraction
        ↓
Inspection JSON + Thermal JSON
        ↓
Evidence Merge Layer
        ↓
Deterministic Severity + Confidence Scoring
        ↓
DDR Generation (Guardrailed LLM)
        ↓
Safety Evaluator (Hallucination Detection)
```

---

## ⭐ Key Features

- **Vision-first** document understanding using multimodal LLMs
- **Structured evidence extraction** from complex, image-heavy PDFs
- **Deterministic severity scoring** — no black-box reasoning
- **Guardrailed report generation** — evidence-only, no hallucination
- **AI safety evaluator** — second model validates report fidelity
- **Modular pipeline** — each stage is independently replaceable
- **Production-oriented** — explainability and scalability built in

---

## 📂 Project Structure
```
DDR_REPORTER/
│
├── extraction.py          # Vision LLM extraction logic
├── confidence.py          # Severity + confidence scoring
├── generation.py          # DDR report generation
├── evaluator.py           # Hallucination safety evaluator
├── main.py                # Pipeline entry point
│
├── prompts/
│   ├── inspection_prompt.txt
│   ├── thermal_prompt.txt
│   └── ddr_prompt.txt
│
├── inputs/
│   ├── inspection_report.pdf
│   └── thermal_report.pdf
│
├── outputs/
│   ├── merged_ddr_data.json
│   ├── scored_merged_ddr_data.json
│   ├── final_ddr.md
│   └── evaluation.json
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/hardik47278/DDR_REPORTER.git
cd DDR_REPORTER
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Poppler (Required for PDF → Image conversion)

This project uses `pdftoppm` from the Poppler library.

- **Windows:** Download from [poppler-windows releases](https://github.com/oschwartz10612/poppler-windows/releases/) and add the `bin/` folder to your system PATH.
- **macOS:** `brew install poppler`
- **Linux:** `sudo apt-get install poppler-utils`

### 5. Set Your OpenAI API Key
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your_api_key_here"

# macOS/Linux
export OPENAI_API_KEY="your_api_key_here"
```

---

## ▶️ Run the Pipeline
```bash
python main.py
```

---

## 🏗️ System Design

This system implements a **reliability-first hybrid AI architecture** for automated property diagnostic reporting. It combines multimodal document understanding (Vision LLMs) with deterministic reasoning layers to ensure structured evidence extraction, explainable severity scoring, and guardrailed report generation. A secondary AI evaluator validates report fidelity to reduce hallucination risk. The modular pipeline supports scalability, human-in-the-loop correction, and integration into production inspection workflows.

---

## 🔮 Roadmap

- [ ] Vision-based room classification for stronger evidence alignment
- [ ] Human-in-the-loop correction interface
- [ ] Knowledge-based repair recommendation engine
- [ ] Async document processing pipeline
- [ ] Batch DDR generation system
- [ ] Graph-based evidence linking
- [ ] Historical inspection comparison via vector memory
