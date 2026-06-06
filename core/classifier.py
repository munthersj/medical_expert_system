def get_range_info(test_info, sex, age_group="adult"):
    """
    Selects the correct reference range.

    Supports age-based structure:

    "ranges": {
        "adult": {
            "male": {...},
            "female": {...}
        },
        "child": {
            "default": {...}
        }
    }

    Also supports the older structure:

    "ranges": {
        "male": {...},
        "female": {...}
    }
    """

    ranges = test_info["ranges"]

    # New age-based structure
    if age_group in ranges:
        age_ranges = ranges[age_group]

        if test_info.get("sex_based") and "male" in age_ranges and "female" in age_ranges:
            return age_ranges[sex]

        if "default" in age_ranges:
            return age_ranges["default"]

    # Fallback to adult ranges if current age group does not exist
    if "adult" in ranges:
        adult_ranges = ranges["adult"]

        if test_info.get("sex_based") and "male" in adult_ranges and "female" in adult_ranges:
            return adult_ranges[sex]

        if "default" in adult_ranges:
            return adult_ranges["default"]

    # Old structure support
    if test_info.get("sex_based"):
        return ranges[sex]

    return ranges["default"]


def classify_standard_numeric(value, test_info, sex, age_group="adult"):
    range_info = get_range_info(test_info, sex, age_group)

    if value < range_info["low_below"]:
        return "low"

    if value > range_info["high_above"]:
        return "high"

    return "normal"


def classify_fasting_glucose(value):
    if value < 70:
        return "low"

    if value <= 99:
        return "normal"

    if 100 <= value <= 125:
        return "prediabetes"

    return "diabetes"


def classify_random_glucose(value):
    if value < 70:
        return "low"

    if value < 200:
        return "normal"

    return "diabetes"


def classify_postprandial_glucose(value):
    """
    Used for:
    - postprandial_glucose
    - ogtt_2h_glucose
    """

    if value < 70:
        return "low"

    if value <= 139:
        return "normal"

    if 140 <= value <= 199:
        return "prediabetes"

    return "diabetes"


def classify_hba1c(value):
    if value <= 5.6:
        return "normal"

    if 5.7 <= value <= 6.4:
        return "prediabetes"

    if value >= 10.0:
        return "very_high"

    return "diabetes"


def classify_value(test_id, value, tests, sex="female", age_group="adult"):
    if test_id not in tests:
        return "unknown"

    test_info = tests[test_id]
    classifier = test_info.get("classifier")

    if classifier == "glucose_fasting":
        return classify_fasting_glucose(value)

    if classifier == "glucose_random":
        return classify_random_glucose(value)

    if classifier == "glucose_postprandial":
        return classify_postprandial_glucose(value)

    if classifier == "hba1c":
        return classify_hba1c(value)

    return classify_standard_numeric(
        value=value,
        test_info=test_info,
        sex=sex,
        age_group=age_group
    )


def classify_values(patient_values, tests, sex="female", age_group="adult"):
    statuses = {}

    for test_id, value in patient_values.items():
        if value is None:
            continue

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            statuses[test_id] = "invalid"
            continue

        statuses[test_id] = classify_value(
            test_id=test_id,
            value=numeric_value,
            tests=tests,
            sex=sex,
            age_group=age_group
        )

    return statuses