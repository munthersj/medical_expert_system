import streamlit as st

from core.analyzer import analyze_patient
from core.loader import load_knowledge_base


st.set_page_config(
    page_title="Medical Expert System",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# Styling
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #11313a 0%, #071318 35%, #05080c 100%);
        color: #EAF7FA;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #061014 0%, #0B1E24 100%);
        border-right: 1px solid rgba(64, 224, 208, 0.18);
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #EAF7FA;
        margin-bottom: 5px;
        animation: fadeSlide 0.8s ease-out;
    }

    .subtitle {
        color: #9FBCC4;
        font-size: 17px;
        margin-bottom: 25px;
        animation: fadeSlide 1s ease-out;
    }

    .glass-card {
        background: rgba(10, 28, 34, 0.72);
        border: 1px solid rgba(64, 224, 208, 0.20);
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(10px);
        animation: fadeUp 0.55s ease-out;
        margin-bottom: 18px;
    }

    .metric-card {
        background: linear-gradient(135deg, rgba(16, 52, 61, 0.95), rgba(7, 22, 28, 0.95));
        border: 1px solid rgba(88, 230, 216, 0.22);
        border-radius: 16px;
        padding: 16px;
        min-height: 125px;
        transition: transform 0.25s ease, border 0.25s ease;
        animation: fadeUp 0.6s ease-out;
        margin-bottom: 14px;
    }

    .metric-card:hover {
        transform: translateY(-4px);
        border: 1px solid rgba(88, 230, 216, 0.55);
    }

    .condition-card {
        background: rgba(9, 24, 30, 0.90);
        border-left: 5px solid #40E0D0;
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 18px;
        box-shadow: 0 10px 26px rgba(0, 0, 0, 0.28);
        animation: fadeUp 0.5s ease-out;
    }

    .danger-card {
        background: rgba(60, 14, 18, 0.9);
        border-left: 5px solid #FF5C70;
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 14px;
        animation: pulseDanger 1.8s infinite;
    }

    .ok-card {
        background: rgba(12, 47, 38, 0.9);
        border-left: 5px solid #54F2A8;
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 14px;
    }

    .tag {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: rgba(64, 224, 208, 0.14);
        color: #72FFF0;
        border: 1px solid rgba(64, 224, 208, 0.25);
        font-size: 12px;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    .small-muted {
        color: #9FBCC4;
        font-size: 13px;
    }

    div[data-testid="stTextInput"] input {
        background-color: rgba(5, 14, 18, 0.85);
        color: #EAF7FA;
        border: 1px solid rgba(64, 224, 208, 0.18);
        border-radius: 10px;
    }

    div[data-testid="stNumberInput"] input {
        background-color: rgba(5, 14, 18, 0.85);
        color: #EAF7FA;
        border: 1px solid rgba(64, 224, 208, 0.18);
        border-radius: 10px;
    }

    .stButton > button {
        background: linear-gradient(90deg, #00C2B8, #2A9DF4);
        color: #031014;
        border: none;
        border-radius: 12px;
        font-weight: 800;
        padding: 0.7rem 1.2rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 22px rgba(64, 224, 208, 0.45);
        color: #031014;
    }

    @keyframes fadeUp {
        from {
            opacity: 0;
            transform: translateY(14px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeSlide {
        from {
            opacity: 0;
            transform: translateX(-18px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes pulseDanger {
        0% {
            box-shadow: 0 0 0 rgba(255, 92, 112, 0.20);
        }
        50% {
            box-shadow: 0 0 18px rgba(255, 92, 112, 0.25);
        }
        100% {
            box-shadow: 0 0 0 rgba(255, 92, 112, 0.20);
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# Helpers
# =========================================================

def safe_float(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    try:
        return float(value)
    except ValueError:
        return "invalid"


def group_tests_by_category(tests):
    grouped = {}

    for test_id, info in tests.items():
        category = info.get("category", "other")

        if info.get("derived"):
            continue

        if category not in grouped:
            grouped[category] = []

        grouped[category].append((test_id, info))

    return grouped


def category_display_name(category):
    names = {
        "cbc": "CBC",
        "cbc_indices": "RBC Indices",
        "platelet_indices": "Platelet Indices",
        "wbc_differential": "WBC Differential",
        "cbc_extended": "CBC Extended",
        "glucose": "Glucose Tests",
        "glucose_monitoring": "Glucose Monitoring",
        "glucose_related": "Glucose Related"
    }

    return names.get(category, category.replace("_", " ").title())


def render_status_badge(status):
    colors = {
        "normal": "#54F2A8",
        "low": "#FFCC66",
        "high": "#FF8A65",
        "prediabetes": "#FFD166",
        "diabetes": "#FF5C70",
        "very_high": "#FF3B5C",
        "invalid": "#FF5C70",
        "unknown": "#9FBCC4"
    }

    color = colors.get(status, "#9FBCC4")

    return (
        f'<span style="'
        f'color:{color};'
        f'border:1px solid {color};'
        f'border-radius:999px;'
        f'padding:4px 10px;'
        f'font-size:12px;'
        f'font-weight:700;'
        f'display:inline-block;'
        f'margin-top:6px;'
        f'">'
        f'{status}'
        f'</span>'
    )

def render_status_card(name, value, unit, status):
    badge = render_status_badge(status)

    return (
        '<div class="metric-card">'
        f'<h4>{name}</h4>'
        f'<p class="small-muted">Value: {value} {unit}</p>'
        f'{badge}'
        '</div>'
    )

def render_condition_card(condition):
    matched_rules = ", ".join(condition.get("matched_rules", []))

    why_items = ""
    for reason in condition.get("why", []):
        why_items += f"<li>{reason}</li>"

    follow_up = ""
    if condition.get("suggested_follow_up_tests"):
        follow_up += "<p><b>Suggested follow-up tests:</b></p><ul>"
        for test in condition["suggested_follow_up_tests"]:
            follow_up += f"<li>{test}</li>"
        follow_up += "</ul>"

    advice = ""
    if condition.get("general_advice"):
        advice += "<p><b>General advice:</b></p><ul>"
        for item in condition["general_advice"]:
            advice += f"<li>{item}</li>"
        advice += "</ul>"

    safety_note = condition.get("safety_note", "")
    safety_html = ""

    if safety_note:
        safety_html = f"<p class='small-muted'><b>Safety note:</b> {safety_note}</p>"

    name = condition.get("name", "Unknown condition")
    score = condition.get("score", 0)
    evidence = condition.get("evidence_level", {}).get("display_name", "Unknown evidence")
    category = condition.get("category", "unknown")
    description = condition.get("description", "")

    return (
        '<div class="condition-card">'
        f'<h3 style="margin-bottom:6px;">{name}</h3>'
        '<div>'
        f'<span class="tag">Score: {score}</span>'
        f'<span class="tag">{evidence}</span>'
        f'<span class="tag">{category}</span>'
        '</div>'
        f'<p class="small-muted">{description}</p>'
        f'<p><b>Matched Rules:</b> {matched_rules}</p>'
        '<p><b>Why?</b></p>'
        f'<ul>{why_items}</ul>'
        f'{follow_up}'
        f'{advice}'
        f'{safety_html}'
        '</div>'
    )


def get_unit_options(kb, tests, test_id):
    info = tests.get(test_id, {})
    default_unit = info.get("unit", "")

    if "units" in kb and test_id in kb["units"]:
        unit_options = list(kb["units"][test_id]["supported_units"].keys())
        default_unit = kb["units"][test_id]["default_unit"]
    else:
        unit_options = [default_unit]

    return unit_options, default_unit


# =========================================================
# Load Knowledge Base
# =========================================================

kb = load_knowledge_base()
tests = kb["tests"]
grouped_tests = group_tests_by_category(tests)


# =========================================================
# Header
# =========================================================

st.markdown(
    """
    <div class="main-title">🩺 Medical Expert System</div>
    <div class="subtitle">
        Dark medical dashboard for CBC and glucose interpretation using an Experta-based expert system.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# Sidebar Patient Info
# =========================================================

with st.sidebar:
    st.markdown("## Patient Info")

    age = st.number_input(
        "Age",
        min_value=0.0,
        max_value=120.0,
        value=25.0,
        step=1.0
    )

    sex = st.selectbox(
        "Sex",
        ["female", "male"]
    )

    st.markdown("---")
    st.markdown("### Notes")
    st.info(
        "This version uses manual input only. OCR will be added later after the core interface is stable."
    )

    st.warning(
        "This system gives preliminary patterns only, not a final diagnosis."
    )


# =========================================================
# Input Form
# =========================================================

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("## Manual Lab Input")
st.markdown(
    '<p class="small-muted">Enter only the values you have. Empty fields will be ignored. Units are converted automatically.</p>',
    unsafe_allow_html=True
)

patient_values = {}

category_order = [
    "cbc",
    "cbc_indices",
    "platelet_indices",
    "wbc_differential",
    "cbc_extended",
    "glucose",
    "glucose_monitoring",
    "glucose_related"
]

existing_categories = [
    category
    for category in category_order
    if category in grouped_tests
]

tabs = st.tabs([
    category_display_name(category)
    for category in existing_categories
])

for tab, category in zip(tabs, existing_categories):
    with tab:
        items = grouped_tests[category]
        cols = st.columns(2)

        for index, (test_id, info) in enumerate(items):
            with cols[index % 2]:
                unit_options, default_unit = get_unit_options(kb, tests, test_id)

                label = f"{info.get('name', test_id)}"
                placeholder = f"Example: {info.get('short_name', test_id)}"

                value_col, unit_col = st.columns([2, 1])

                with value_col:
                    value = st.text_input(
                        label=label,
                        placeholder=placeholder,
                        key=f"input_{test_id}"
                    )

                with unit_col:
                    selected_unit = st.selectbox(
                        "Unit",
                        unit_options,
                        index=unit_options.index(default_unit) if default_unit in unit_options else 0,
                        key=f"unit_{test_id}"
                    )

                parsed = safe_float(value)

                if parsed == "invalid":
                    st.error(f"Invalid value for {info.get('name', test_id)}")
                elif parsed is not None:
                    patient_values[test_id] = {
                        "value": parsed,
                        "unit": selected_unit
                    }

                st.caption(info.get("description", ""))

st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# Analyze Button
# =========================================================

analyze_clicked = st.button("Analyze Results", type="primary")


# =========================================================
# Results
# =========================================================

if analyze_clicked:
    invalid_values = []

    for test_id in tests:
        raw_value = st.session_state.get(f"input_{test_id}", "")
        parsed = safe_float(raw_value)

        if parsed == "invalid":
            invalid_values.append(test_id)

    if invalid_values:
        st.error("Please fix invalid numeric values before analysis.")
        st.write(invalid_values)
        st.stop()

    if not patient_values:
        st.warning("Please enter at least one lab value.")
        st.stop()

    try:
        report = analyze_patient(
            patient_values=patient_values,
            sex=sex,
            age=age
        )
    except Exception as e:
        st.error("An error occurred while analyzing the results.")
        st.code(str(e))
        st.stop()

    st.markdown("## Analysis Report")

    # Summary
    st.markdown(
        f"""
        <div class="glass-card">
            <h3>Summary</h3>
            <p>{report["summary"]}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Patient context
    context = report["patient_context"]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>Sex</h4>
                <h2>{context["sex"]}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>Age</h4>
                <h2>{context["age"]}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>Age Group</h4>
                <h2>{context["age_group"]}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Urgent patterns
    st.markdown("### Urgent Patterns")

    urgent_patterns = report.get("urgent_patterns", [])

    if urgent_patterns:
        for condition in urgent_patterns:
            why_html = ""
            for reason in condition.get("why", []):
                why_html += f"<li>{reason}</li>"

            st.markdown(
                f"""
                <div class="danger-card">
                    <h3>{condition.get("name")}</h3>
                    <p>{condition.get("description")}</p>
                    <p><b>Score:</b> {condition.get("score")}</p>
                    <p><b>Why?</b></p>
                    <ul>{why_html}</ul>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            """
            <div class="ok-card">
                <h4>No urgent warning pattern detected</h4>
                <p>Based on the currently covered expert rules only.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Unit conversion summary
    st.markdown("### Unit Conversion Summary")

    normalized_values = report.get("normalized_values", {})
    raw_input_values = report.get("raw_input_values", {})
    original_units = report.get("original_units", {})

    conversion_items = []

    for test_id, normalized_value in normalized_values.items():
        info = tests.get(test_id, {})
        default_unit = info.get("unit", "")

        raw_value = raw_input_values.get(test_id)
        original_unit = original_units.get(test_id)

        if isinstance(raw_value, dict):
            display_raw_value = raw_value.get("value")
            display_raw_unit = raw_value.get("unit")
        else:
            display_raw_value = raw_value
            display_raw_unit = original_unit or default_unit

        conversion_items.append({
            "test": info.get("name", test_id),
            "input": f"{display_raw_value} {display_raw_unit or ''}",
            "normalized": f"{normalized_value} {default_unit}"
        })

    if conversion_items:
        cols = st.columns(3)

        for index, item in enumerate(conversion_items):
            with cols[index % 3]:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <h4>{item["test"]}</h4>
                        <p class="small-muted">Input: {item["input"]}</p>
                        <p class="small-muted">Normalized: {item["normalized"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("No unit conversion data available.")

    # Classified statuses
    st.markdown("### Classified Statuses")

    status_items = list(report["classified_statuses"].items())

    if status_items:
        cols = st.columns(3)

        for index, (test_id, status) in enumerate(status_items):
            info = tests.get(test_id, {})
            name = info.get("name", test_id)
            unit = info.get("unit", "")
            value = report["input_values"].get(test_id, "")

            with cols[index % 3]:
                st.markdown(
                    render_status_card(
                        name=name,
                        value=value,
                        unit=unit,
                        status=status
                    ),
                    unsafe_allow_html=True
                )

    # Possible conditions
    st.markdown("### Possible Conditions / Patterns")

    regular_patterns = report.get("regular_patterns", [])

    if not regular_patterns:
        st.info("No regular covered pattern detected.")
    else:
        for condition in regular_patterns:
            st.markdown(
                render_condition_card(condition),
                unsafe_allow_html=True
            )

    # Disclaimer
    st.markdown("### Disclaimer")
    st.markdown(
        f"""
        <div class="glass-card">
            <p>{report["disclaimer"]}</p>
        </div>
        """,
        unsafe_allow_html=True
    )