from core.loader import load_knowledge_base
from core.patient_context import build_patient_context
from core.unit_converter import normalize_patient_values
from core.derived_values import calculate_derived_values
from core.classifier import classify_values
from core.experta_engine import run_experta_engine
from core.scorer import calculate_condition_scores
from core.report_builder import build_report
from core.validator import validate_knowledge_base


def analyze_patient(patient_values, sex="female", age=None, validate_kb=True):
    kb = load_knowledge_base()

    if validate_kb:
        errors = validate_knowledge_base(kb)
        if errors:
            joined = "\n".join(errors)
            raise ValueError(f"Knowledge base validation failed:\n{joined}")

    patient_context = build_patient_context(
        sex=sex,
        age=age
    )

    normalized_values, original_units = normalize_patient_values(
        patient_values=patient_values,
        units_config=kb["units"]
    )

    values_with_derived = calculate_derived_values(normalized_values)

    statuses = classify_values(
        patient_values=values_with_derived,
        tests=kb["tests"],
        sex=patient_context["sex"],
        age_group=patient_context["age_group"]
    )

    matched_rules = run_experta_engine(
        statuses=statuses,
        patient_values=values_with_derived,
        patient_context=patient_context
    )

    condition_scores = calculate_condition_scores(matched_rules)

    # Red flags are now handled inside Experta as urgent_medical_attention_pattern
    red_flag_warnings = []

    report = build_report(
        patient_context=patient_context,
        patient_values=values_with_derived,
        statuses=statuses,
        condition_scores=condition_scores,
        red_flag_warnings=red_flag_warnings,
        conditions=kb["conditions"],
        severity_levels=kb["severity_levels"]
    )

    report["raw_input_values"] = patient_values
    report["normalized_values"] = normalized_values
    report["values_with_derived"] = values_with_derived
    report["original_units"] = original_units

    return report