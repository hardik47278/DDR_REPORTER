# src/reasoning/confidence_scoring.py

def compute_severity_and_confidence(merged_json):
    """
    Adds severity_level, confidence_score, conflict, and reasoning_note
    to each item inside merged_area_evidence.

    Input:
        merged_json = {
            ...,
            "merged_area_evidence": [...],
            "unmatched_thermal_readings": [...]
        }

    Output:
        same dict with scored merged_area_evidence
    """

    area_items = merged_json.get("merged_area_evidence", [])
    scored_items = []

    for item in area_items:
        negative = str(item.get("negative_side", "")).lower()
        positive = str(item.get("positive_side", "")).lower()
        thermal_list = item.get("matched_thermal_readings", [])

        # --------------------------------
        # Build combined issue text
        # --------------------------------
        issue_text = f"{negative} {positive}".strip()

        # --------------------------------
        # Build thermal summary text
        # --------------------------------
        thermal_parts = []
        for t in thermal_list:
            interpretation = str(t.get("interpretation", ""))
            hotspot = str(t.get("hotspot_celsius", ""))
            coldspot = str(t.get("coldspot_celsius", ""))
            location_hint = str(t.get("location_hint", ""))

            thermal_parts.append(
                f"{interpretation} hotspot:{hotspot} coldspot:{coldspot} location:{location_hint}"
            )

        thermal_text = " | ".join(thermal_parts).lower()

        # --------------------------------
        # Defaults
        # --------------------------------
        severity = "Low"
        score = 0.50
        conflict = False
        reasons = []

        # --------------------------------
        # Inspection-based severity rules
        # --------------------------------
        if any(word in issue_text for word in ["crack", "seepage", "leakage", "leak"]):
            severity = "High"
            score += 0.25
            reasons.append("Structural/water ingress keyword detected")

        if any(word in issue_text for word in ["damp", "dampness", "efflorescence", "moisture"]):
            if severity != "High":
                severity = "Medium"
            score += 0.15
            reasons.append("Moisture-related issue")

        if "ceiling" in issue_text:
            score += 0.05
            reasons.append("Ceiling involvement noted")

        if "bathroom" in issue_text or "wc" in issue_text or "outlet leakage" in issue_text:
            score += 0.05
            reasons.append("Wet-area source indicated")

        # --------------------------------
        # Thermal rules
        # --------------------------------
        if thermal_list:
            score += 0.10
            reasons.append("Thermal evidence linked to area")

            if any(
                phrase in thermal_text
                for phrase in ["active moisture", "thermal anomaly", "hotspot"]
            ):
                severity = "High"
                score += 0.20
                reasons.append("Thermal anomaly / active moisture detected")
        else:
            score -= 0.10
            reasons.append("No matched thermal confirmation")

        # --------------------------------
        # Conflict rules
        # --------------------------------
        # Example: inspection sounds mild but thermal says strong moisture
        mild_terms = ["minor", "slight", "light"]
        strong_thermal_terms = ["active moisture", "thermal anomaly", "hotspot"]

        if any(term in negative for term in mild_terms) and any(term in thermal_text for term in strong_thermal_terms):
            conflict = True
            score -= 0.20
            reasons.append("Conflict between mild inspection wording and stronger thermal signal")

        # --------------------------------
        # Clamp
        # --------------------------------
        score = max(0.0, min(score, 1.0))

        # --------------------------------
        # Save enriched item
        # --------------------------------
        enriched = dict(item)
        enriched["conflict"] = conflict
        enriched["severity_level"] = severity
        enriched["confidence_score"] = round(score, 2)
        enriched["reasoning_note"] = ", ".join(reasons) if reasons else "Rule-based assessment"

        scored_items.append(enriched)

    merged_json["merged_area_evidence"] = scored_items
    return merged_json
