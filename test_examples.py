import json
from pathlib import Path
from core.analyzer import analyze_patient

def main():
    with open(Path("examples/sample_patients.json"), "r", encoding="utf-8") as f:
        examples = json.load(f)
    for name, patient in examples.items():
        print("\n" + "#"*80)
        print("CASE:", name)
        print("#"*80)
        report = analyze_patient(
            patient_values=patient["values"],
            sex=patient["sex"],
            age=patient.get("age", 25)
        )
        print("Summary:", report["summary"])
        print("Statuses:", report["classified_statuses"])
        print("Red flags:", report["red_flags"])
        print("Possible conditions:")
        for c in report["possible_conditions"]:
            print("-", c["name"], "| Score:", c["score"], "| Level:", c["evidence_level"]["display_name"])

if __name__ == "__main__":
    main()
