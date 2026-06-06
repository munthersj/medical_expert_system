from core.scorer import get_score_level


DISCLAIMER = (
    "This expert system provides preliminary decision-support information only. "
    "It does not provide a final medical diagnosis and cannot rule out conditions "
    "outside its knowledge base. Reference ranges may vary by lab, age, sex, "
    "pregnancy status, and clinical context. A healthcare professional should "
    "review abnormal results."
)


def build_report(
    patient_context,
    patient_values,
    statuses,
    condition_scores,
    red_flag_warnings,
    conditions,
    severity_levels
):
    possible_conditions = []

    for condition_id, score_data in condition_scores.items():
        condition_info = conditions.get(condition_id, {})
        score = score_data["score"]
        level = get_score_level(score, severity_levels)

        possible_conditions.append({
            "condition_id": condition_id,
            "name": condition_info.get("name", condition_id),
            "category": condition_info.get("category", ""),
            "type": condition_info.get("type", "pattern"),
            "description": condition_info.get("description", ""),
            "score": score,
            "evidence_level": level,
            "matched_rules": score_data["matched_rules"],
            "why": score_data["explanations"],
            "possible_causes": condition_info.get("possible_causes", []),
            "suggested_follow_up_tests": condition_info.get("suggested_follow_up_tests", []),
            "general_advice": condition_info.get("general_advice", []),
            "safety_note": condition_info.get("safety_note", ""),
            "sources": score_data.get("sources", [])
        })

    possible_conditions.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    urgent_patterns = [
        condition
        for condition in possible_conditions
        if condition["condition_id"] == "urgent_medical_attention_pattern"
    ]

    regular_patterns = [
        condition
        for condition in possible_conditions
        if condition["condition_id"] != "urgent_medical_attention_pattern"
    ]

    abnormal_tests = {
        test: status
        for test, status in statuses.items()
        if status not in ["normal"]
    }

    if urgent_patterns:
        summary = "Urgent warning patterns were detected. Medical review may be needed."
    elif regular_patterns:
        summary = "Some possible patterns were detected based on the current knowledge base."
    elif abnormal_tests:
        summary = "Abnormal values were detected, but no covered pattern reached enough evidence."
    else:
        summary = "No abnormal covered pattern was detected based on the current knowledge base."

    return {
        "summary": summary,
        "patient_context": patient_context,
        "input_values": patient_values,
        "classified_statuses": statuses,
        "abnormal_tests": abnormal_tests,
        "possible_conditions": possible_conditions,
        "urgent_patterns": urgent_patterns,
        "regular_patterns": regular_patterns,
        "red_flags": red_flag_warnings,
        "disclaimer": DISCLAIMER
    }