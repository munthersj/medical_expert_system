REQUIRED_RULE_FIELDS = ["id", "condition_id", "when", "weight", "explanation", "active"]
SUPPORTED_OPERATORS = ["<", ">", "<=", ">=", "=="]

def validate_condition_expression(expression, tests):
    errors = []
    for key in ["all", "any", "not"]:
        conditions = expression.get(key, [])
        if not isinstance(conditions, list):
            errors.append(f"'{key}' must be a list.")
            continue
        for condition in conditions:
            test = condition.get("test")
            if not test:
                errors.append(f"Condition inside '{key}' is missing test.")
                continue
            if test not in tests:
                errors.append(f"Unknown test in rule condition: {test}")
            has_status = "status" in condition
            has_status_in = "status_in" in condition
            if not has_status and not has_status_in:
                errors.append(f"Condition for test '{test}' must have status or status_in.")
            if has_status_in and not isinstance(condition["status_in"], list):
                errors.append(f"status_in for test '{test}' must be a list.")
    if "min_matched" in expression:
        try:
            if int(expression["min_matched"]) < 1:
                errors.append("min_matched must be >= 1.")
        except (TypeError, ValueError):
            errors.append("min_matched must be an integer.")
    return errors

def validate_knowledge_base(kb):
    errors = []
    tests = kb["tests"]
    conditions = kb["conditions"]
    rules = kb["rules"]
    red_flags = kb["red_flags"]
    units = kb.get("units", {})
    rule_ids = set()
    for rule in rules:
        for field in REQUIRED_RULE_FIELDS:
            if field not in rule:
                errors.append(f"Rule is missing required field '{field}': {rule}")
        rule_id = rule.get("id")
        if rule_id in rule_ids:
            errors.append(f"Duplicate rule id: {rule_id}")
        rule_ids.add(rule_id)
        condition_id = rule.get("condition_id")
        if condition_id and condition_id not in conditions:
            errors.append(f"Rule {rule_id} references unknown condition_id: {condition_id}")
        if "when" in rule:
            errors.extend([f"Rule {rule_id}: {error}" for error in validate_condition_expression(rule["when"], tests)])
        if "weight" in rule:
            try:
                if float(rule["weight"]) <= 0:
                    errors.append(f"Rule {rule_id} weight must be positive.")
            except (TypeError, ValueError):
                errors.append(f"Rule {rule_id} weight must be numeric.")
    flag_ids = set()
    for flag in red_flags:
        flag_id = flag.get("id")
        if flag_id in flag_ids:
            errors.append(f"Duplicate red flag id: {flag_id}")
        flag_ids.add(flag_id)
        test = flag.get("test")
        if test not in tests:
            errors.append(f"Red flag {flag_id} references unknown test: {test}")
        if flag.get("operator") not in SUPPORTED_OPERATORS:
            errors.append(f"Red flag {flag_id} has unsupported operator: {flag.get('operator')}")
        try:
            float(flag.get("value"))
        except (TypeError, ValueError):
            errors.append(f"Red flag {flag_id} value must be numeric.")
    errors.extend(validate_units(tests, units))

    return errors
def validate_units(tests, units):
    errors = []

    for test_id, unit_info in units.items():
        if test_id not in tests:
            errors.append(f"units.json references unknown test: {test_id}")
            continue

        if "default_unit" not in unit_info:
            errors.append(f"Unit config for {test_id} is missing default_unit.")

        if "supported_units" not in unit_info:
            errors.append(f"Unit config for {test_id} is missing supported_units.")
            continue

        supported_units = unit_info["supported_units"]

        if not isinstance(supported_units, dict):
            errors.append(f"supported_units for {test_id} must be an object.")
            continue

        default_unit = unit_info.get("default_unit")

        if default_unit not in supported_units:
            errors.append(
                f"default_unit '{default_unit}' for {test_id} is not listed in supported_units."
            )

        for unit_name, conversion in supported_units.items():
            if not isinstance(conversion, dict):
                errors.append(f"Conversion rule for {test_id}/{unit_name} must be an object.")
                continue

            has_factor = "factor" in conversion
            has_formula = "formula" in conversion

            if not has_factor and not has_formula:
                errors.append(
                    f"Conversion rule for {test_id}/{unit_name} must have factor or formula."
                )

            if has_factor:
                try:
                    float(conversion["factor"])
                except (TypeError, ValueError):
                    errors.append(
                        f"factor for {test_id}/{unit_name} must be numeric."
                    )

            if "offset" in conversion:
                try:
                    float(conversion["offset"])
                except (TypeError, ValueError):
                    errors.append(
                        f"offset for {test_id}/{unit_name} must be numeric."
                    )

    return errors
