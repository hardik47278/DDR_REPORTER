from openai import OpenAI, RateLimitError
import json
import time
import re

client = OpenAI(api_key="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")


def serialize_data(data):
    try:
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        return str(data)


def extract_retry_after_seconds(error_text):
    match = re.search(r"try again in\s*([0-9.]+)s", error_text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return 2.0


def build_ddr_messages(structured_data, base_prompt):
    guardrail_rules = """
STRICT VALIDATION RULES:

1. NEVER invent information.
2. Use ONLY provided structured data.
3. If any field is missing, write "Not Available".
4. If conflict = true, mention the conflict clearly.
5. Do NOT add engineering assumptions beyond the evidence.
6. Use simple, professional, client-friendly language.
7. Do NOT output JSON.
8. If thermal evidence is unmatched or unavailable, say so clearly.
9. Base severity discussion only on provided severity_level and confidence_score.
10. Mention area-wise findings clearly.
"""

    system_message = f"""
{base_prompt}

{guardrail_rules}

Write the report in clear sections:
1. Property Information
2. Inspection Summary
3. Thermal Summary
4. Area-wise Observations
5. Overall Assessment
6. Limitations / Missing Information
7. Conclusion
"""

    user_message = f"""
STRUCTURED OBSERVATION DATA:
{serialize_data(structured_data)}

Generate the final Detailed Diagnostic Report.
"""

    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]


def fallback_generate_ddr(structured_data):
    return "Offline fallback DDR generation used because API was unavailable."


def generate_ddr(structured_data, prompt, max_retries=5):
    messages = build_ddr_messages(structured_data, prompt)

    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                temperature=0.2,
                messages=messages
            )

            report = response.choices[0].message.content

            if not report or len(report.strip()) < 50:
                raise ValueError("DDR output too short")

            return report

        except RateLimitError as e:
            err_text = str(e)
            wait_time = extract_retry_after_seconds(err_text)
            print(f"⚠️ DDR rate limit hit. Retry {attempt}/{max_retries} after {wait_time:.2f}s")
            if attempt == max_retries:
                print("Switching to OFFLINE DDR generation:", e)
                return fallback_generate_ddr(structured_data)
            time.sleep(wait_time)

        except Exception as e:
            print("Switching to OFFLINE DDR generation:", e)
            return fallback_generate_ddr(structured_data)
