from core.analyzer import analyze_patient


def print_report(report):
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(report["summary"])

    print("\nPATIENT CONTEXT")
    print("-" * 70)
    context = report["patient_context"]
    print(f"Sex: {context['sex']}")
    print(f"Age: {context['age']}")
    print(f"Age group: {context['age_group']}")

    print("\nRAW INPUT VALUES")
    print("-" * 70)
    for test, value in report.get("raw_input_values", {}).items():
        print(f"{test}: {value}")

    print("\nNORMALIZED VALUES")
    print("-" * 70)
    for test, value in report.get("normalized_values", {}).items():
        print(f"{test}: {value}")

    print("\nVALUES WITH DERIVED")
    print("-" * 70)
    for test, value in report.get("values_with_derived", {}).items():
        print(f"{test}: {value}")

    print("\nCLASSIFIED STATUSES")
    print("-" * 70)
    for test, status in report["classified_statuses"].items():
        print(f"{test}: {status}")

    print("\nURGENT PATTERNS")
    print("-" * 70)
    if not report.get("urgent_patterns"):
        print("No urgent warning pattern detected based on current expert rules.")
    else:
        for condition in report["urgent_patterns"]:
            print(f"\n{condition['name']}")
            print(f"Score: {condition['score']}")
            print("Matched Rules:", ", ".join(condition["matched_rules"]))
            print("Why:")
            for reason in condition["why"]:
                print(f"- {reason}")

    print("\nPOSSIBLE CONDITIONS / PATTERNS")
    print("-" * 70)

    regular_patterns = report.get("regular_patterns", [])

    if not regular_patterns:
        print("No regular covered pattern detected.")
    else:
        for condition in regular_patterns:
            print(f"\n{condition['name']}")
            print(
                f"Score: {condition['score']} | "
                f"Evidence: {condition['evidence_level']['display_name']}"
            )
            print("Matched Rules:", ", ".join(condition["matched_rules"]))

            print("Why:")
            for reason in condition["why"]:
                print(f"- {reason}")

            if condition.get("suggested_follow_up_tests"):
                print("Suggested follow-up tests:")
                for test in condition["suggested_follow_up_tests"]:
                    print(f"- {test}")

            if condition.get("general_advice"):
                print("General advice:")
                for advice in condition["general_advice"]:
                    print(f"- {advice}")

            if condition.get("safety_note"):
                print("Safety note:")
                print(condition["safety_note"])

    print("\nDISCLAIMER")
    print("-" * 70)
    print(report["disclaimer"])


if __name__ == "__main__":
    sample_patient = {
        "hemoglobin": {
            "value": 101,
            "unit": "g/L"
        },
        "hematocrit": {
            "value": 33,
            "unit": "%"
        },
        "rbc": {
            "value": 4.0,
            "unit": "million cells/mcL"
        },
        "wbc": {
            "value": 15.5,
            "unit": "10^9/L"
        },
        "platelets": {
            "value": 350,
            "unit": "10^9/L"
        },
        "mcv": {
            "value": 72,
            "unit": "fL"
        },
        "mch": {
            "value": 24,
            "unit": "pg"
        },
        "mchc": {
            "value": 310,
            "unit": "g/L"
        },
        "rdw": {
            "value": 16.0,
            "unit": "%"
        },
        "neutrophils_percent": {
            "value": 82,
            "unit": "%"
        },
        "lymphocytes_percent": {
            "value": 12,
            "unit": "%"
        },
        "eosinophils_percent": {
            "value": 2,
            "unit": "%"
        },
        "fasting_glucose": {
            "value": 7.9,
            "unit": "mmol/L"
        },
        "hba1c": {
            "value": 55,
            "unit": "mmol/mol"
        }
    }

    report = analyze_patient(
        patient_values=sample_patient,
        sex="female",
        age=25
    )

    print_report(report)