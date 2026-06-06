def calculate_derived_values(patient_values):
    """
    Adds derived WBC differential absolute values when possible.

    Expected:
    - wbc in cells/mcL
    - percentages as percent values, e.g. 65 for 65%

    Derived:
    - anc = wbc * neutrophils_percent / 100
    - alc = wbc * lymphocytes_percent / 100
    - aec = wbc * eosinophils_percent / 100
    - absolute_monocytes = wbc * monocytes_percent / 100
    - absolute_basophils = wbc * basophils_percent / 100
    """

    values = dict(patient_values)

    wbc = values.get("wbc")

    if wbc is None:
        return values

    try:
        wbc = float(wbc)
    except (TypeError, ValueError):
        return values

    derived_map = {
        "anc": "neutrophils_percent",
        "alc": "lymphocytes_percent",
        "aec": "eosinophils_percent",
        "absolute_monocytes": "monocytes_percent",
        "absolute_basophils": "basophils_percent"
    }

    for derived_test, percent_test in derived_map.items():
        if derived_test in values:
            continue

        percent = values.get(percent_test)

        if percent is None:
            continue

        try:
            percent = float(percent)
        except (TypeError, ValueError):
            continue

        values[derived_test] = round(wbc * percent / 100.0, 2)

    return values