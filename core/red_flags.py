def compare(value, operator, threshold):
    if operator == "<": return value < threshold
    if operator == ">": return value > threshold
    if operator == "<=": return value <= threshold
    if operator == ">=": return value >= threshold
    if operator == "==": return value == threshold
    raise ValueError(f"Unsupported operator: {operator}")

def check_red_flags(patient_values, red_flags):
    warnings = []
    for flag in red_flags:
        if not flag.get("active", True): continue
        test_id = flag["test"]
        if test_id not in patient_values: continue
        value = float(patient_values[test_id])
        threshold = float(flag["value"])
        if compare(value, flag["operator"], threshold):
            warnings.append({"id":flag["id"],"test":test_id,"message":flag["message"],"severity":flag.get("severity","warning")})
    return warnings
