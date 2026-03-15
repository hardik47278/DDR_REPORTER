from openai import OpenAI, RateLimitError
import json
import time
import re

client = OpenAI(api_key="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")


def serialize(data):
    try:
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        return str(data)


def extract_retry_after_seconds(error_text):
    match = re.search(r"try again in\s*([0-9.]+)s", error_text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return 2.0


def evaluate_ddr(structured_data, generated_ddr, max_retries=5):
    evaluator_prompt = """
You are an AI Safety Evaluator.

Your job is to verify whether the Detailed Diagnostic Report (DDR)
contains information NOT present in the structured data.

VALIDATION RULES:
1. If DDR introduces new facts not supported by structured data, mark hallucination=true.
2. If missing data exists but DDR did not write "Not Available" or clearly acknowledge limitation, mark missing_rule_violation=true.
3. If structured data shows conflict=true but DDR does not mention the conflict, mark conflict_ignored=true.
4. Be strict and conservative.

Return ONLY JSON:
{
  "hallucination": false,
  "missing_rule_violation": false,
  "conflict_ignored": false,
  "notes": ""
}
"""

    user_message = f"""
STRUCTURED DATA:
{serialize(structured_data)}

DDR OUTPUT:
{generated_ddr}
"""

    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                temperature=0,
                messages=[
                    {"role": "system", "content": evaluator_prompt},
                    {"role": "user", "content": user_message}
                ]
            )

            content = response.choices[0].message.content

            try:
                return json.loads(content)
            except Exception:
                start = content.find("{")
                end = content.rfind("}") + 1
                return json.loads(content[start:end])

        except RateLimitError as e:
            err_text = str(e)
            wait_time = extract_retry_after_seconds(err_text)
            print(f"⚠️ Evaluator rate limit hit. Retry {attempt}/{max_retries} after {wait_time:.2f}s")
            if attempt == max_retries:
                print("⚠️ Evaluator switched to OFFLINE mode:", e)
                return {
                    "hallucination": None,
                    "missing_rule_violation": None,
                    "conflict_ignored": None,
                    "notes": "Offline evaluation mode: evaluator could not verify DDR."
                }
            time.sleep(wait_time)

        except Exception as e:
            print("⚠️ Evaluator switched to OFFLINE mode:", e)
            return {
                "hallucination": None,
                "missing_rule_violation": None,
                "conflict_ignored": None,
                "notes": "Offline evaluation mode: evaluator could not verify DDR."
            }
