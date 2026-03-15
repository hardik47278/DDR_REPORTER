# 🏠 AI Detailed Diagnostic Report (DDR) Generator — Vision Hybrid Pipeline

An AI-powered system that automatically generates **Detailed Diagnostic Reports (DDR)** for property inspections by combining:

- Inspection report PDF (text + images)
- Thermal imaging report PDF
- Vision LLM structured extraction
- Deterministic reasoning (severity + confidence scoring)
- Guardrailed DDR generation
- Hallucination evaluation layer

This project follows a **Reliability-First Hybrid AI Architecture** where structured evidence is extracted first and then reasoning + report generation are performed.

🧠 Stage-Wise Explanation

1. Input Documents
The system accepts two PDFs:
- Inspection Report (contains visual observations and checklist findings)
- Thermal Imaging Report (contains thermal scan evidence)

2. PDF Page Conversion
Each PDF page is converted into high-resolution images using pdftoppm.
This enables multimodal AI models to analyze visual layout, tables, and photos.

3. Vision-LLM Structured Evidence Extraction
A multimodal LLM processes page images and extracts structured JSON including:
- Property information
- Area-wise inspection observations
- Thermal scan readings
- Device metadata

4. Evidence Alignment & Merge Layer
Inspection evidence and thermal evidence are aligned using location hints,
surface context, and keyword similarity to create unified area-wise evidence.

5. Rule-Based Severity & Confidence Scoring
A deterministic reasoning layer assigns:
- severity_level (Low / Medium / High)
- confidence_score (0–1)
based on structural keywords, moisture indicators, thermal anomalies, and conflicts.

6. Guardrailed DDR Report Generation
An LLM generates a client-ready Detailed Diagnostic Report using strict rules:
- Use only structured evidence
- Do not hallucinate
- Clearly mark missing information
- Mention conflicts explicitly

7. AI Safety Evaluator
A second LLM validates the generated DDR by checking:
- hallucinated facts
- ignored missing data
- ignored evidence conflicts
and produces an evaluation JSON.

🏗️ System Design Summary (Professional Paragraph)

This system implements a reliability-first hybrid AI architecture for automated property diagnostic reporting. 
It combines multimodal document understanding using Vision-LLMs with deterministic reasoning layers to ensure 
structured evidence extraction, explainable severity scoring, and guardrailed report generation. A secondary 
AI evaluator further validates report fidelity, reducing hallucination risk. The modular pipeline design 
supports scalability, human-in-the-loop correction, and potential integration into production inspection workflows.






---

## 🚀 Pipeline Architecture

Inspection PDF + Thermal PDF
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
DDR Generation (LLM Guardrailed)
        ↓
Safety Evaluator (Hallucination Detection)

⭐ Key Features
- Vision-First document understanding using multimodal LLMs
- Structured evidence extraction from complex PDFs
- Deterministic severity and confidence reasoning layer
- Guardrailed natural-language DDR generation
- AI safety evaluator for hallucination detection
- Modular pipeline architecture
- Production-oriented design with explainability focus

- 





---

## 📂 Project Structure

DDR_REPORTER/
│
├── extraction.py
├── confidence.py
├── generation.py
├── evaluator.py
├── main.py
│
├── prompts/
│ ├── inspection_prompt.txt
│ ├── thermal_prompt.txt
│ └── ddr_prompt.txt
│
├── inputs/
│ ├── inspection_report.pdf
│ └── thermal_report.pdf
│
├── outputs/
│ ├── merged_ddr_data.json
│ ├── scored_merged_ddr_data.json
│ ├── final_ddr.md
│ └── evaluation.json
│
├── requirements.txt
└── README.md



---

## ⚙️ Installation

### Clone Repo

```bash
git clone https://github.com/hardik47278/DDR_REPORTER.git
cd DDR_REPORTER


python -m venv venv
venv\Scripts\activate


python -m venv venv
venv\Scripts\activate

📌 Install Poppler (Required)

This project uses pdftoppm for converting PDF pages into images.

Download Poppler:
https://github.com/oschwartz10612/poppler-windows/releases/

🔑 Set OpenAI API Key

PowerShell:

$env:OPENAI_API_KEY="your_api_key_here"

▶️ Run Pipeline
python main.py


🧩 Future Improvements Section

- Vision-based room classification for stronger evidence alignment
- Human-in-the-loop correction interface
- Knowledge-based repair recommendation engine
- Async document processing pipeline
- Batch DDR generation system
- Graph-based evidence linking
- Historical inspection comparison using vector memory




























