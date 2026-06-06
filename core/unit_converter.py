def normalize_unit_name(unit):
    if unit is None:
        return None

    unit = str(unit).strip()

    replacements = {
        "μ": "µ",
        "ul": "uL",
        "µl": "µL",
        "microL": "µL",
        "mcL": "mcL",
        "mmol/l": "mmol/L",
        "mg/dl": "mg/dL",
        "g/dl": "g/dL",
        "g/l": "g/L",
        "iu": "IU"
    }

    lower_unit = unit.lower()

    if lower_unit in replacements:
        return replacements[lower_unit]

    return unit


def convert_hba1c_ifcc_to_ngsp(value):
    """
    Converts HbA1c IFCC mmol/mol to NGSP %.

    Approximate formula:
    NGSP (%) = 0.09148 × IFCC + 2.152
    """
    return 0.09148 * value + 2.152


def convert_value(test_id, value, from_unit, units_config):
    if test_id not in units_config:
        return float(value)

    test_units = units_config[test_id]
    default_unit = test_units["default_unit"]
    supported_units = test_units["supported_units"]

    from_unit = normalize_unit_name(from_unit)

    if from_unit is None:
        from_unit = default_unit

    if from_unit not in supported_units:
        raise ValueError(
            f"Unsupported unit '{from_unit}' for test '{test_id}'. "
            f"Supported units: {list(supported_units.keys())}"
        )

    rule = supported_units[from_unit]

    value = float(value)

    if "formula" in rule:
        if test_id == "hba1c" and rule["formula"] == "ifcc_to_ngsp":
            return round(convert_hba1c_ifcc_to_ngsp(value), 3)

        raise ValueError(f"Unsupported conversion formula: {rule['formula']}")

    factor = float(rule.get("factor", 1))
    offset = float(rule.get("offset", 0))

    converted_value = value * factor + offset

    return round(converted_value, 3)


def normalize_patient_values(patient_values, units_config):
    """
    Accepts two input styles:

    1. Old simple style:
       {
           "hemoglobin": 10.5,
           "wbc": 7800
       }

    2. Unit-aware style:
       {
           "hemoglobin": {"value": 105, "unit": "g/L"},
           "wbc": {"value": 7.8, "unit": "10^9/L"},
           "fasting_glucose": {"value": 7.0, "unit": "mmol/L"}
       }

    Returns values converted to the default units used by tests.json.
    """

    normalized = {}
    original_units = {}

    for test_id, raw_value in patient_values.items():
        if raw_value is None:
            continue

        if isinstance(raw_value, dict):
            value = raw_value.get("value")
            unit = raw_value.get("unit")
        else:
            value = raw_value
            unit = None

        if value is None or value == "":
            continue

        converted_value = convert_value(
            test_id=test_id,
            value=value,
            from_unit=unit,
            units_config=units_config
        )

        normalized[test_id] = converted_value
        original_units[test_id] = unit

    return normalized, original_units