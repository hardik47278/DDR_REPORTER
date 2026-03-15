import os
import json
import base64
import subprocess
import time
import re
from pathlib import Path
from io import BytesIO

from PIL import Image
from openai import OpenAI, RateLimitError





# =========================================================
# CONFIG
# =========================================================
INSPECTION_PDF = r"D:\urbanroof\inputs\Sample_Report.pdf"
THERMAL_PDF = r"D:\urbanroof\inputs\Thermal Images.pdf"

OUTPUT_DIR = r"D:\urbanroof\outputs"
INSPECTION_IMG_DIR = os.path.join(OUTPUT_DIR, "inspection_pages")
THERMAL_IMG_DIR = os.path.join(OUTPUT_DIR, "thermal_pages")

MODEL = "gpt-4o-mini"
DPI = 150
MAX_PAGES_PER_PDF = 10   # keep small for now

# Retry / pacing settings
MAX_RETRIES = 6
BASE_DELAY_SECONDS = 3
BETWEEN_CALLS_DELAY = 5   # wait between inspection and thermal requests

# IMPORTANT:
# Put your NEW key in environment variable OPENAI_API_KEY
# PowerShell:
# $env:OPENAI_API_KEY="your-new-key"
client = OpenAI(api_key="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")


# =========================================================
# PDF EXTRACTOR
# =========================================================
class PDFExtractor:
    """Convert PDF pages to JPG images and encode images for OpenAI."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_pages(self, pdf_path: str, prefix: str, dpi: int = DPI) -> list[str]:
        print(f"\n📄 Extracting pages from: {pdf_path}")

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        out_prefix = str(self.output_dir / prefix)

        cmd = [
            "pdftoppm",
            "-jpeg",
            "-r", str(dpi),
            pdf_path,
            out_prefix
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(
                f"pdftoppm failed.\nSTDERR:\n{result.stderr}"
            )

        img_paths = sorted(str(p) for p in self.output_dir.glob(f"{prefix}*.jpg"))

        print(f"✅ Extracted {len(img_paths)} page images")
        return img_paths[:MAX_PAGES_PER_PDF]

    def image_to_base64(self, img_path: str, max_width: int = 1200) -> str:
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Image not found: {img_path}")

        with Image.open(img_path) as img:
            if img.width > max_width:
                ratio = max_width / img.width
                new_h = int(img.height * ratio)
                img = img.resize((max_width, new_h), Image.LANCZOS)

            if img.mode != "RGB":
                img = img.convert("RGB")

            buf = BytesIO()
            img.save(buf, format="JPEG", quality=75)
            return base64.b64encode(buf.getvalue()).decode("utf-8")


# =========================================================
# OPENAI ANALYZER
# =========================================================
class AIAnalyzerOpenAI:
    def __init__(self, model: str = MODEL):
        self.model = model

    def _safe_json(self, text: str):
        text = text.strip()

        try:
            return json.loads(text)
        except Exception:
            pass

        start_list = text.find("[")
        end_list = text.rfind("]") + 1
        if start_list != -1 and end_list > start_list:
            try:
                return json.loads(text[start_list:end_list])
            except Exception:
                pass

        start_obj = text.find("{")
        end_obj = text.rfind("}") + 1
        if start_obj != -1 and end_obj > start_obj:
            try:
                return json.loads(text[start_obj:end_obj])
            except Exception:
                pass

        raise ValueError("Could not parse model output as JSON.\nOutput was:\n" + text)

    def _extract_retry_after_seconds(self, error_text: str) -> float | None:
        """
        Parse OpenAI error text like:
        'Please try again in 2.295s'
        """
        match = re.search(r"try again in\s*([0-9.]+)s", error_text, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return None

    def _responses_create_with_retry(self, content: list):
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                print(f"📡 OpenAI request attempt {attempt}/{MAX_RETRIES} ...")
                response = client.responses.create(
                    model=self.model,
                    input=[{"role": "user", "content": content}]
                )
                return response

            except RateLimitError as e:
                err_text = str(e)

                suggested_wait = self._extract_retry_after_seconds(err_text)
                backoff_wait = BASE_DELAY_SECONDS * (2 ** (attempt - 1))
                wait_time = max(suggested_wait or 0, backoff_wait)

                print(f"⚠️ Rate limit hit on attempt {attempt}")
                print(f"   Error: {err_text}")
                print(f"   Waiting {wait_time:.2f} seconds before retry...")

                if attempt == MAX_RETRIES:
                    raise

                time.sleep(wait_time)

            except Exception as e:
                print(f"❌ Non-rate-limit error on attempt {attempt}: {e}")
                if attempt == MAX_RETRIES:
                    raise
                wait_time = BASE_DELAY_SECONDS * attempt
                print(f"   Waiting {wait_time:.2f} seconds before retry...")
                time.sleep(wait_time)

        raise RuntimeError("Unexpected retry flow exit.")

    def analyze_inspection_report(self, page_images: list[str], extractor: PDFExtractor) -> dict:
        print("\n🤖 Sending inspection pages to OpenAI Vision...")

        content = [
            {
                "type": "input_text",
                "text": """
You are analyzing a property inspection report.

Extract information into ONLY valid JSON.

Return this exact JSON schema:
{
  "property_info": {
    "property_type": "",
    "floors": "",
    "inspection_date": "",
    "inspected_by": "",
    "score": "",
    "flagged_items": "",
    "previous_audit": "",
    "previous_repair": "",
    "customer_name": "Not Available",
    "address": "Not Available"
  },
  "impacted_areas": [
    {
      "area_number": 1,
      "negative_side": "description of visible damage",
      "positive_side": "description of likely source/root area",
      "page_numbers_negative": [1],
      "page_numbers_positive": [2]
    }
  ],
  "checklist_findings": [
    {
      "item": "item name",
      "result": "Yes/No/Moderate/N/A"
    }
  ],
  "missing_info": []
}

Rules:
- Return ONLY JSON
- Do not use markdown
- If unclear, write "Not Available"
- Do not invent values
"""
            }
        ]

        for img_path in page_images:
            b64 = extractor.image_to_base64(img_path)
            content.append({
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{b64}",
                "detail": "high"
            })

        response = self._responses_create_with_retry(content)
        return self._safe_json(response.output_text)

    def analyze_thermal_report(self, page_images: list[str], extractor: PDFExtractor) -> dict:
        print("\n🌡️ Sending thermal pages to OpenAI Vision...")

        content = [
            {
                "type": "input_text",
                "text": """
You are analyzing a thermal imaging property inspection report.

Extract information into ONLY valid JSON.

Return this exact JSON schema:
{
  "device": "",
  "serial_number": "",
  "inspection_date": "",
  "emissivity": "",
  "reflected_temperature": "",
  "thermal_readings": [
    {
      "image_id": "RB02380X.JPG",
      "page_number": 1,
      "hotspot_celsius": "",
      "coldspot_celsius": "",
      "delta_celsius": "",
      "location_hint": "skirting/wall/ceiling/window/door area description",
      "interpretation": "active moisture / suspect moisture / no visible moisture / Not Available"
    }
  ]
}

Rules:
- Return ONLY JSON
- Do not use markdown
- Extract all visible thermal readings from the provided pages
- If unclear, write "Not Available"
- Do not invent values
"""
            }
        ]

        for img_path in page_images:
            b64 = extractor.image_to_base64(img_path)
            content.append({
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{b64}",
                "detail": "high"
            })

        response = self._responses_create_with_retry(content)
        return self._safe_json(response.output_text)


# =========================================================
# MERGE LOGIC
# =========================================================
def merge_inspection_and_thermal(inspection_data: dict, thermal_data: dict) -> dict:
    impacted_areas = inspection_data.get("impacted_areas", [])
    thermal_readings = thermal_data.get("thermal_readings", [])

    merged_areas = []

    for area in impacted_areas:
        neg_text = str(area.get("negative_side", "")).lower()
        pos_text = str(area.get("positive_side", "")).lower()
        combined_text = f"{neg_text} {pos_text}"

        matched_thermal = []

        for tr in thermal_readings:
            hint = str(tr.get("location_hint", "")).lower()

            keywords = [
                "wall", "skirting", "ceiling", "window", "door",
                "floor", "bathroom", "toilet", "kitchen", "hall", "bedroom"
            ]
            common = [k for k in keywords if k in combined_text and k in hint]

            if common:
                matched_thermal.append(tr)

        merged_areas.append({
            "area_number": area.get("area_number"),
            "negative_side": area.get("negative_side", "Not Available"),
            "positive_side": area.get("positive_side", "Not Available"),
            "page_numbers_negative": area.get("page_numbers_negative", []),
            "page_numbers_positive": area.get("page_numbers_positive", []),
            "matched_thermal_readings": matched_thermal
        })

    merged = {
        "property_info": inspection_data.get("property_info", {}),
        "checklist_findings": inspection_data.get("checklist_findings", []),
        "missing_info": inspection_data.get("missing_info", []),
        "thermal_report_info": {
            "device": thermal_data.get("device", "Not Available"),
            "serial_number": thermal_data.get("serial_number", "Not Available"),
            "inspection_date": thermal_data.get("inspection_date", "Not Available"),
            "emissivity": thermal_data.get("emissivity", "Not Available"),
            "reflected_temperature": thermal_data.get("reflected_temperature", "Not Available"),
        },
        "merged_area_evidence": merged_areas,
        "unmatched_thermal_readings": thermal_readings
    }

    return merged


# =========================================================
# SAVE HELPER
# =========================================================
def save_json(data, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved: {path}")


# =========================================================
# MAIN
# =========================================================
def main():
    

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    inspection_extractor = PDFExtractor(INSPECTION_IMG_DIR)
    thermal_extractor = PDFExtractor(THERMAL_IMG_DIR)
    analyzer = AIAnalyzerOpenAI()

    # 1) PDF -> page images
    inspection_pages = inspection_extractor.extract_pages(
        pdf_path=INSPECTION_PDF,
        prefix="inspection_page_"
    )

    thermal_pages = thermal_extractor.extract_pages(
        pdf_path=THERMAL_PDF,
        prefix="thermal_page_"
    )

    print("\n🖼️ Inspection pages used:")
    for p in inspection_pages:
        print("   ", p)

    print("\n🖼️ Thermal pages used:")
    for p in thermal_pages:
        print("   ", p)

    # 2) OpenAI Vision extraction
    inspection_json = analyzer.analyze_inspection_report(
        inspection_pages,
        inspection_extractor
    )

    print(f"\n⏳ Waiting {BETWEEN_CALLS_DELAY}s before thermal request...")
    time.sleep(BETWEEN_CALLS_DELAY)

    thermal_json = analyzer.analyze_thermal_report(
        thermal_pages,
        thermal_extractor
    )

    # 3) Save raw outputs
    inspection_json_path = os.path.join(OUTPUT_DIR, "inspection_extracted.json")
    thermal_json_path = os.path.join(OUTPUT_DIR, "thermal_extracted.json")

    save_json(inspection_json, inspection_json_path)
    save_json(thermal_json, thermal_json_path)

    # 4) Merge
    merged_json = merge_inspection_and_thermal(inspection_json, thermal_json)
    merged_json_path = os.path.join(OUTPUT_DIR, "merged_ddr_data.json")
    save_json(merged_json, merged_json_path)

    # 5) Print in terminal
    print("\n" + "=" * 80)
    print("✅ INSPECTION JSON")
    print("=" * 80)
    print(json.dumps(inspection_json, indent=2, ensure_ascii=False))

    print("\n" + "=" * 80)
    print("✅ THERMAL JSON")
    print("=" * 80)
    print(json.dumps(thermal_json, indent=2, ensure_ascii=False))

    print("\n" + "=" * 80)
    print("✅ MERGED JSON")
    print("=" * 80)
    print(json.dumps(merged_json, indent=2, ensure_ascii=False))

    print("\n🎉 Done.")


if __name__ == "__main__":
    main()
