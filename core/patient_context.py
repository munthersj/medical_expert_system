def get_age_group(age):
    """
    Converts numeric age into a general age group.

    Current version:
    - adult ranges are fully supported
    - child/adolescent/newborn are detected but not fully supported in tests.json yet
    """

    if age is None:
        return "adult"

    try:
        age = float(age)
    except (TypeError, ValueError):
        return "adult"

    if age < 0:
        return "adult"

    if age < 1:
        return "newborn"

    if age < 13:
        return "child"

    if age < 18:
        return "adolescent"

    return "adult"


def build_patient_context(sex="female", age=None):
    if sex not in ["male", "female"]:
        raise ValueError("sex must be 'male' or 'female'.")

    age_group = get_age_group(age)

    return {
        "sex": sex,
        "age": age,
        "age_group": age_group
    }