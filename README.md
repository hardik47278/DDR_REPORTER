# 🏠 AI Detailed Diagnostic Report (DDR) Generator — Vision Hybrid Pipeline

This project builds an AI-powered pipeline that automatically generates a **Detailed Diagnostic Report (DDR)** for property inspections by combining:

- Inspection report PDF (text + images)
- Thermal imaging report PDF
- Vision LLM extraction
- Deterministic reasoning (severity + confidence scoring)
- Guardrailed DDR generation
- Hallucination evaluation layer

The system follows a **reliability-first hybrid architecture** where structured evidence is extracted first, then reasoning and report generation are performed.

---

## 🚀 Pipeline Architecture

Inspection PDF
Thermal PDF
↓
PDF → Page Images (pdftoppm)
↓
Vision LLM Structured Extraction
↓
Inspection JSON + Thermal JSON
↓
Evidence Merge
↓
Deterministic Severity + Confidence Scoring
↓
DDR Generation (LLM with Guardrails)
↓
Safety Evaluator (Hallucination Detection)


---

## 📂 Project Structure


project-root/
│
├── extraction.py # Vision extraction + merge pipeline
├── confidence.py # Severity & confidence reasoning layer
├── generation.py # DDR generator (LLM)
├── evaluator.py # Guardrail evaluation layer
├── main.py # End-to-end orchestrator
│
├── prompts/
│ ├── inspection_prompt.txt
│ ├── thermal_prompt.txt
│ └── ddr_prompt.txt
│
├── data/
│ ├── inspection_report.pdf
│ └── thermal_report.pdf
│
├── outputs/
│ ├── merged_ddr_data.json
│ ├── scored_merged_ddr_data.json
│ ├── final_ddr.md
│ └── evaluation.json
│
└── requirements.txt


---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone <repo-url>
cd <repo>
2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Install Poppler (Required)

This project uses pdftoppm to convert PDF pages into images.

Windows

Download Poppler:
https://github.com/oschwartz10612/poppler-windows/releases/

Add Library/bin folder to PATH.

Example:

C:\poppler\Library\bin
5️⃣ Set OpenAI API Key

PowerShell:

$env:OPENAI_API_KEY="your_api_key_here"
▶️ Run Pipeline
python main.py
📄 Output Files
File	Description
merged_ddr_data.json	Structured inspection + thermal evidence
scored_merged_ddr_data.json	Evidence with severity + confidence
final_ddr.md	Generated Detailed Diagnostic Report
evaluation.json	Hallucination & rule-violation analysis
🧠 Key Design Decisions
✅ Vision-First Extraction

Instead of relying only on OCR/text parsing, the system converts PDF pages into images and uses a multimodal LLM to extract structured evidence.

✅ Deterministic Reasoning Layer

Severity and confidence scoring are rule-based to ensure consistency and explainability.

✅ Guardrailed Report Generation

The DDR generator is instructed to:

Never invent information

Use only structured evidence

Clearly mark missing data

Mention conflicts explicitly

✅ Safety Evaluator

A second LLM validates the DDR for:

hallucinated facts

ignored missing information

ignored evidence conflicts

📊 Example Use Cases

Property inspection diagnostics

Insurance claim validation

Leakage / seepage analysis

Building condition reporting

AI-assisted site audit documentation

⚠️ Limitations

Thermal images may not always map clearly to inspection areas

Missing metadata reduces evidence correlation accuracy

LLM outputs depend on quality of extracted structured evidence

Requires OpenAI API usage and rate-limit handling

🔮 Future Improvements

Vision-based room classification

Human-in-the-loop correction UI

Graph-based evidence linking

Repair recommendation knowledge base

Batch processing for multiple properties

Async + streaming pipeline

Vector memory for historical inspection comparison

👨‍💻 Author

Hardik Anand
Aspiring AI / Data Science Engineer
Focus: Production-grade RAG & Vision-LLM Systems


---


