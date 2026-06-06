
import collections
import collections.abc

if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping

from experta import KnowledgeEngine, Fact, Rule, MATCH, OR, AND, NOT, TEST


class LabStatus(Fact):
    """
    Represents a classified lab value.

    Example:
    LabStatus(test="hemoglobin", status="low")
    LabStatus(test="mcv", status="low")
    LabStatus(test="hba1c", status="diabetes")
    """
    pass


class LabValue(Fact):
    """
    Represents the original numeric value.

    Example:
    LabValue(test="hemoglobin", value=10.1)
    """
    pass


class PatientInfo(Fact):
    """
    Represents patient context.

    Example:
    PatientInfo(sex="female", age=25, age_group="adult")
    """
    pass


class MedicalExpertEngine(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.matched_rules = []

    def add_rule_result(self, rule_id, condition_id, weight, explanation, source="Medical expert rule"):
        for rule in self.matched_rules:
            if rule["id"] == rule_id:
                return

        self.matched_rules.append({
            "id": rule_id,
            "condition_id": condition_id,
            "weight": weight,
            "explanation": explanation,
            "source": source
        })

    # =========================================================
    # ANEMIA BASIC RULES
    # =========================================================

    @Rule(
        OR(
            LabStatus(test="hemoglobin", status="low"),
            LabStatus(test="hematocrit", status="low"),
            LabStatus(test="rbc", status="low")
        )
    )
    def possible_anemia_pattern(self):
        self.add_rule_result(
            rule_id="EX_R001",
            condition_id="possible_anemia_pattern",
            weight=4,
            explanation="One or more red blood cell measurements are low, which may suggest an anemia pattern.",
            source="Experta rule: anemia screening"
        )

    @Rule(
        LabStatus(test="hemoglobin", status="low"),
        LabStatus(test="mcv", status="low")
    )
    def microcytic_anemia_pattern(self):
        self.add_rule_result(
            rule_id="EX_R002",
            condition_id="microcytic_anemia_pattern",
            weight=6,
            explanation="Low hemoglobin together with low MCV supports a microcytic anemia pattern.",
            source="Experta rule: microcytic anemia pattern"
        )

    @Rule(
        LabStatus(test="mch", status="low"),
        OR(
            LabStatus(test="mchc", status="low"),
            LabStatus(test="rdw", status="high")
        )
    )
    def microcytic_supporting_indices(self):
        self.add_rule_result(
            rule_id="EX_R003",
            condition_id="microcytic_anemia_pattern",
            weight=3,
            explanation="Low MCH with low MCHC or high RDW may support a microcytic or hypochromic pattern.",
            source="Experta rule: RBC indices support microcytosis"
        )

    @Rule(
        LabStatus(test="hemoglobin", status="low"),
        LabStatus(test="mcv", status="high")
    )
    def macrocytic_anemia_pattern(self):
        self.add_rule_result(
            rule_id="EX_R004",
            condition_id="macrocytic_anemia_pattern",
            weight=6,
            explanation="Low hemoglobin together with high MCV supports a macrocytic anemia pattern.",
            source="Experta rule: macrocytic anemia pattern"
        )

    @Rule(
        LabStatus(test="hemoglobin", status="low"),
        LabStatus(test="mcv", status="normal")
    )
    def normocytic_anemia_pattern(self):
        self.add_rule_result(
            rule_id="EX_R005",
            condition_id="normocytic_anemia_pattern",
            weight=5,
            explanation="Low hemoglobin with normal MCV supports a normocytic anemia pattern.",
            source="Experta rule: normocytic anemia pattern"
        )

    @Rule(
        LabStatus(test="hemoglobin", status="low"),
        LabStatus(test="reticulocytes_percent", status="low")
    )
    def anemia_low_reticulocytes(self):
        self.add_rule_result(
            rule_id="EX_R006",
            condition_id="possible_anemia_pattern",
            weight=4,
            explanation="Low hemoglobin with low reticulocytes may suggest reduced red blood cell production.",
            source="Experta rule: anemia with low reticulocyte response"
        )

    @Rule(
        LabStatus(test="hemoglobin", status="low"),
        LabStatus(test="reticulocytes_percent", status="high")
    )
    def anemia_high_reticulocytes(self):
        self.add_rule_result(
            rule_id="EX_R007",
            condition_id="possible_anemia_pattern",
            weight=4,
            explanation="Low hemoglobin with high reticulocytes may suggest increased red blood cell loss or destruction.",
            source="Experta rule: anemia with high reticulocyte response"
        )

    # =========================================================
    # POLYCYTHEMIA / HIGH RBC RULES
    # =========================================================

    @Rule(
        OR(
            LabStatus(test="hemoglobin", status="high"),
            LabStatus(test="hematocrit", status="high"),
            LabStatus(test="rbc", status="high")
        )
    )
    def possible_polycythemia_pattern(self):
        self.add_rule_result(
            rule_id="EX_R008",
            condition_id="possible_polycythemia_pattern",
            weight=4,
            explanation="One or more red blood cell measurements are high, which may suggest increased red cell concentration.",
            source="Experta rule: polycythemia screening"
        )

    # =========================================================
    # WBC AND INFECTION / INFLAMMATION RULES
    # =========================================================

    @Rule(
        LabStatus(test="wbc", status="high")
    )
    def possible_infection_inflammation_pattern(self):
        self.add_rule_result(
            rule_id="EX_R009",
            condition_id="possible_infection_inflammation_pattern",
            weight=4,
            explanation="WBC is high, which may suggest infection, inflammation, stress response, or other causes.",
            source="Experta rule: high WBC"
        )

    @Rule(
        LabStatus(test="wbc", status="high"),
        OR(
            LabStatus(test="anc", status="high"),
            LabStatus(test="neutrophils_percent", status="high")
        )
    )
    def infection_with_neutrophilia(self):
        self.add_rule_result(
            rule_id="EX_R010",
            condition_id="possible_infection_inflammation_pattern",
            weight=4,
            explanation="High WBC together with neutrophilia strengthens infection or inflammation evidence.",
            source="Experta rule: high WBC with neutrophilia"
        )

    @Rule(
        LabStatus(test="wbc", status="low")
    )
    def possible_low_wbc_pattern(self):
        self.add_rule_result(
            rule_id="EX_R011",
            condition_id="possible_low_wbc_pattern",
            weight=4,
            explanation="WBC is low and needs medical interpretation.",
            source="Experta rule: low WBC"
        )

    @Rule(
        OR(
            LabStatus(test="anc", status="high"),
            LabStatus(test="neutrophils_percent", status="high")
        )
    )
    def possible_neutrophilia_pattern(self):
        self.add_rule_result(
            rule_id="EX_R012",
            condition_id="possible_neutrophilia_pattern",
            weight=5,
            explanation="Neutrophil count or percentage is high, which may support bacterial infection, inflammation, stress, or medication effect.",
            source="Experta rule: neutrophilia"
        )

    @Rule(
        LabStatus(test="anc", status="low")
    )
    def possible_neutropenia_pattern(self):
        self.add_rule_result(
            rule_id="EX_R013",
            condition_id="possible_neutropenia_pattern",
            weight=6,
            explanation="Absolute neutrophil count is low, which may suggest neutropenia.",
            source="Experta rule: neutropenia"
        )

    @Rule(
        OR(
            LabStatus(test="alc", status="high"),
            LabStatus(test="lymphocytes_percent", status="high")
        )
    )
    def possible_lymphocytosis_pattern(self):
        self.add_rule_result(
            rule_id="EX_R014",
            condition_id="possible_lymphocytosis_pattern",
            weight=5,
            explanation="Lymphocyte count or percentage is high, which may support viral or immune-related patterns.",
            source="Experta rule: lymphocytosis"
        )

    @Rule(
        OR(
            LabStatus(test="aec", status="high"),
            LabStatus(test="eosinophils_percent", status="high")
        )
    )
    def possible_eosinophilia_pattern(self):
        self.add_rule_result(
            rule_id="EX_R015",
            condition_id="possible_eosinophilia_pattern",
            weight=5,
            explanation="Eosinophil count or percentage is high, which may support allergy, asthma, parasite exposure, medication reaction, or other causes.",
            source="Experta rule: eosinophilia"
        )

    # =========================================================
    # PLATELET RULES
    # =========================================================

    @Rule(
        LabStatus(test="platelets", status="low")
    )
    def possible_thrombocytopenia_pattern(self):
        self.add_rule_result(
            rule_id="EX_R016",
            condition_id="possible_thrombocytopenia_pattern",
            weight=5,
            explanation="Platelet count is low, which may suggest a thrombocytopenia pattern.",
            source="Experta rule: thrombocytopenia"
        )

    @Rule(
        LabStatus(test="platelets", status="high")
    )
    def possible_thrombocytosis_pattern(self):
        self.add_rule_result(
            rule_id="EX_R017",
            condition_id="possible_thrombocytosis_pattern",
            weight=5,
            explanation="Platelet count is high, which may suggest a thrombocytosis pattern.",
            source="Experta rule: thrombocytosis"
        )

    @Rule(
        LabStatus(test="platelets", status="low"),
        LabStatus(test="mpv", status="high")
    )
    def thrombocytopenia_with_high_mpv(self):
        self.add_rule_result(
            rule_id="EX_R018",
            condition_id="possible_thrombocytopenia_pattern",
            weight=3,
            explanation="Low platelets with high MPV may suggest increased platelet turnover, but clinical interpretation is required.",
            source="Experta rule: low platelets with high MPV"
        )

    # =========================================================
    # COMBINED CYTOPENIA RULES
    # =========================================================

    @Rule(
        LabStatus(test="hemoglobin", status="low"),
        LabStatus(test="wbc", status="low")
    )
    def combined_cytopenia_hb_wbc(self):
        self.add_rule_result(
            rule_id="EX_R019",
            condition_id="possible_combined_cytopenia_pattern",
            weight=6,
            explanation="Hemoglobin and WBC are both low, suggesting more than one blood cell line may be affected.",
            source="Experta rule: combined cytopenia"
        )

    @Rule(
        LabStatus(test="hemoglobin", status="low"),
        LabStatus(test="platelets", status="low")
    )
    def combined_cytopenia_hb_platelets(self):
        self.add_rule_result(
            rule_id="EX_R020",
            condition_id="possible_combined_cytopenia_pattern",
            weight=6,
            explanation="Hemoglobin and platelets are both low, suggesting more than one blood cell line may be affected.",
            source="Experta rule: combined cytopenia"
        )

    @Rule(
        LabStatus(test="wbc", status="low"),
        LabStatus(test="platelets", status="low")
    )
    def combined_cytopenia_wbc_platelets(self):
        self.add_rule_result(
            rule_id="EX_R021",
            condition_id="possible_combined_cytopenia_pattern",
            weight=6,
            explanation="WBC and platelets are both low, suggesting more than one blood cell line may be affected.",
            source="Experta rule: combined cytopenia"
        )

    # =========================================================
    # GLUCOSE RULES
    # =========================================================

    @Rule(
        OR(
            LabStatus(test="fasting_glucose", status="low"),
            LabStatus(test="random_glucose", status="low"),
            LabStatus(test="postprandial_glucose", status="low"),
            LabStatus(test="ogtt_2h_glucose", status="low")
        )
    )
    def possible_hypoglycemia_pattern(self):
        self.add_rule_result(
            rule_id="EX_R022",
            condition_id="possible_hypoglycemia_pattern",
            weight=6,
            explanation="One glucose value is low, which may suggest hypoglycemia.",
            source="Experta rule: hypoglycemia"
        )

    @Rule(
        OR(
            LabStatus(test="fasting_glucose", status="prediabetes"),
            LabStatus(test="hba1c", status="prediabetes"),
            LabStatus(test="postprandial_glucose", status="prediabetes"),
            LabStatus(test="ogtt_2h_glucose", status="prediabetes")
        )
    )
    def possible_prediabetes_pattern(self):
        self.add_rule_result(
            rule_id="EX_R023",
            condition_id="possible_prediabetes_pattern",
            weight=4,
            explanation="At least one glucose-related value is in the prediabetes range.",
            source="Experta rule: prediabetes pattern"
        )

    @Rule(
        LabStatus(test="fasting_glucose", status="prediabetes"),
        LabStatus(test="hba1c", status="prediabetes")
    )
    def stronger_prediabetes_pattern(self):
        self.add_rule_result(
            rule_id="EX_R024",
            condition_id="possible_prediabetes_pattern",
            weight=4,
            explanation="Both fasting glucose and HbA1c are in the prediabetes range, increasing evidence.",
            source="Experta rule: multiple prediabetes indicators"
        )

    @Rule(
        OR(
            LabStatus(test="fasting_glucose", status="diabetes"),
            LabStatus(test="random_glucose", status="diabetes"),
            LabStatus(test="postprandial_glucose", status="diabetes"),
            LabStatus(test="ogtt_2h_glucose", status="diabetes"),
            LabStatus(test="hba1c", status="diabetes"),
            LabStatus(test="hba1c", status="very_high")
        )
    )
    def possible_diabetes_pattern(self):
        self.add_rule_result(
            rule_id="EX_R025",
            condition_id="possible_diabetes_pattern",
            weight=5,
            explanation="At least one glucose-related value is in the diabetes range and needs clinical confirmation.",
            source="Experta rule: diabetes pattern"
        )

    @Rule(
        LabStatus(test="fasting_glucose", status="diabetes"),
        OR(
            LabStatus(test="hba1c", status="diabetes"),
            LabStatus(test="hba1c", status="very_high")
        )
    )
    def stronger_diabetes_pattern(self):
        self.add_rule_result(
            rule_id="EX_R026",
            condition_id="possible_diabetes_pattern",
            weight=5,
            explanation="Both fasting glucose and HbA1c are in the diabetes range, increasing evidence.",
            source="Experta rule: multiple diabetes indicators"
        )

    @Rule(
        LabStatus(test="hba1c", status="very_high")
    )
    def poor_long_term_glucose_control(self):
        self.add_rule_result(
            rule_id="EX_R027",
            condition_id="possible_poor_long_term_glucose_control",
            weight=7,
            explanation="HbA1c is very high, suggesting poor long-term glucose control.",
            source="Experta rule: very high HbA1c"
        )

    @Rule(
        LabStatus(test="fructosamine", status="high")
    )
    def high_fructosamine_pattern(self):
        self.add_rule_result(
            rule_id="EX_R028",
            condition_id="possible_poor_long_term_glucose_control",
            weight=4,
            explanation="Fructosamine is high, which may suggest elevated short-term average glucose depending on lab method and clinical context.",
            source="Experta rule: high fructosamine"
        )

    @Rule(
        LabStatus(test="fasting_glucose", status="normal"),
        OR(
            LabStatus(test="hba1c", status="diabetes"),
            LabStatus(test="hba1c", status="very_high")
        )
    )
    def discordant_glucose_normal_fasting_high_a1c(self):
        self.add_rule_result(
            rule_id="EX_R029",
            condition_id="possible_discordant_glucose_results",
            weight=5,
            explanation="Fasting glucose is normal while HbA1c is in diabetes range; this discordance needs review.",
            source="Experta rule: discordant glucose results"
        )

    @Rule(
        LabStatus(test="fasting_glucose", status="diabetes"),
        LabStatus(test="hba1c", status="normal")
    )
    def discordant_glucose_high_fasting_normal_a1c(self):
        self.add_rule_result(
            rule_id="EX_R030",
            condition_id="possible_discordant_glucose_results",
            weight=5,
            explanation="Fasting glucose is in diabetes range while HbA1c is normal; this discordance needs review.",
            source="Experta rule: discordant glucose results"
        )

    # =========================================================
    # RED FLAGS AS EXPERTA RULES
    # =========================================================

    @Rule(
        LabValue(test="hemoglobin", value=MATCH.value),
        TEST(lambda value: value < 7.0)
    )
    def urgent_low_hemoglobin(self, value):
        self.add_rule_result(
            rule_id="EX_F001",
            condition_id="urgent_medical_attention_pattern",
            weight=10,
            explanation="Very low hemoglobin may require urgent medical attention.",
            source="Experta red flag rule"
        )

    def run_experta_engine(statuses, patient_values=None, patient_context=None):
        if patient_values is None:
            patient_values = {}

        if patient_context is None:
            patient_context = {}

        engine = MedicalExpertEngine()
        engine.reset()

        if patient_context:
            engine.declare(PatientInfo(
                sex=patient_context.get("sex"),
                age=patient_context.get("age"),
                age_group=patient_context.get("age_group")
            ))

        for test, status in statuses.items():
            engine.declare(LabStatus(
                test=test,
                status=status
            ))

        for test, value in patient_values.items():
            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                continue

            engine.declare(LabValue(
                test=test,
                value=numeric_value
            ))

        engine.run()

        return engine.matched_rules
    # =========================================================
    # RED FLAGS AS EXPERTA RULES
    # =========================================================

    @Rule(
        LabValue(test="hemoglobin", value=MATCH.value),
        TEST(lambda value: value < 7.0)
    )
    def urgent_low_hemoglobin(self, value):
        self.add_rule_result(
            rule_id="EX_F001",
            condition_id="urgent_medical_attention_pattern",
            weight=10,
            explanation="Very low hemoglobin may require urgent medical attention, especially with shortness of breath, chest pain, fainting, or severe weakness.",
            source="Experta red flag rule: hemoglobin < 7.0"
        )

    @Rule(
        LabValue(test="wbc", value=MATCH.value),
        TEST(lambda value: value > 30000)
    )
    def urgent_very_high_wbc(self, value):
        self.add_rule_result(
            rule_id="EX_F002",
            condition_id="urgent_medical_attention_pattern",
            weight=10,
            explanation="Very high WBC may require urgent medical evaluation, especially with fever or severe symptoms.",
            source="Experta red flag rule: WBC > 30000"
        )

    @Rule(
        LabValue(test="wbc", value=MATCH.value),
        TEST(lambda value: value < 2000)
    )
    def urgent_very_low_wbc(self, value):
        self.add_rule_result(
            rule_id="EX_F003",
            condition_id="urgent_medical_attention_pattern",
            weight=10,
            explanation="Very low WBC may increase infection risk and should be reviewed urgently, especially if fever is present.",
            source="Experta red flag rule: WBC < 2000"
        )

    @Rule(
        LabValue(test="platelets", value=MATCH.value),
        TEST(lambda value: value < 50000)
    )
    def urgent_low_platelets(self, value):
        self.add_rule_result(
            rule_id="EX_F004",
            condition_id="urgent_medical_attention_pattern",
            weight=10,
            explanation="Very low platelets may increase bleeding risk and need urgent medical review, especially with bleeding or bruising.",
            source="Experta red flag rule: platelets < 50000"
        )

    @Rule(
        LabValue(test="platelets", value=MATCH.value),
        TEST(lambda value: value > 1000000)
    )
    def urgent_extremely_high_platelets(self, value):
        self.add_rule_result(
            rule_id="EX_F005",
            condition_id="urgent_medical_attention_pattern",
            weight=10,
            explanation="Extremely high platelets may require urgent medical evaluation.",
            source="Experta red flag rule: platelets > 1000000"
        )

    @Rule(
        LabValue(test="anc", value=MATCH.value),
        TEST(lambda value: value < 500)
    )
    def urgent_very_low_anc(self, value):
        self.add_rule_result(
            rule_id="EX_F006",
            condition_id="urgent_medical_attention_pattern",
            weight=10,
            explanation="Very low ANC may be urgent, especially if fever is present.",
            source="Experta red flag rule: ANC < 500"
        )

    @Rule(
        LabValue(test="fasting_glucose", value=MATCH.value),
        TEST(lambda value: value < 54)
    )
    def urgent_low_fasting_glucose(self, value):
        self.add_rule_result(
            rule_id="EX_F007",
            condition_id="urgent_medical_attention_pattern",
            weight=10,
            explanation="Very low fasting glucose can be urgent, especially with confusion, fainting, seizure, or inability to eat or drink.",
            source="Experta red flag rule: fasting glucose < 54"
        )

    @Rule(
        LabValue(test="random_glucose", value=MATCH.value),
        TEST(lambda value: value < 54)
    )
    def urgent_low_random_glucose(self, value):
        self.add_rule_result(
            rule_id="EX_F008",
            condition_id="urgent_medical_attention_pattern",
            weight=10,
            explanation="Very low random glucose can be urgent, especially with confusion, fainting, seizure, or inability to eat or drink.",
            source="Experta red flag rule: random glucose < 54"
        )

    @Rule(
        LabValue(test="postprandial_glucose", value=MATCH.value),
        TEST(lambda value: value < 54)
    )
    def urgent_low_postprandial_glucose(self, value):
        self.add_rule_result(
            rule_id="EX_F009",
            condition_id="urgent_medical_attention_pattern",
            weight=10,
            explanation="Very low postprandial glucose can be urgent, especially with confusion, fainting, seizure, or inability to eat or drink.",
            source="Experta red flag rule: postprandial glucose < 54"
        )

    @Rule(
        LabValue(test="ogtt_2h_glucose", value=MATCH.value),
        TEST(lambda value: value < 54)
    )
    def urgent_low_ogtt_glucose(self, value):
        self.add_rule_result(
            rule_id="EX_F010",
            condition_id="urgent_medical_attention_pattern",
            weight=10,
            explanation="Very low 2-hour OGTT glucose can be urgent, especially with confusion, fainting, seizure, or inability to eat or drink.",
            source="Experta red flag rule: OGTT 2h glucose < 54"
        )

    @Rule(
        OR(
            LabValue(test="random_glucose", value=MATCH.value),
            LabValue(test="postprandial_glucose", value=MATCH.value),
            LabValue(test="ogtt_2h_glucose", value=MATCH.value)
        ),
        TEST(lambda value: value > 300)
    )
    def urgent_very_high_nonfasting_glucose(self, value):
        self.add_rule_result(
            rule_id="EX_F011",
            condition_id="urgent_medical_attention_pattern",
            weight=10,
            explanation="Very high non-fasting glucose may require urgent medical advice, especially with vomiting, dehydration, confusion, or rapid breathing.",
            source="Experta red flag rule: non-fasting glucose > 300"
        )

    @Rule(
        LabValue(test="fasting_glucose", value=MATCH.value),
        TEST(lambda value: value > 250)
    )
    def warning_very_high_fasting_glucose(self, value):
        self.add_rule_result(
            rule_id="EX_F012",
            condition_id="urgent_medical_attention_pattern",
            weight=8,
            explanation="Very high fasting glucose may require prompt medical evaluation.",
            source="Experta red flag rule: fasting glucose > 250"
        )

    @Rule(
        LabValue(test="hba1c", value=MATCH.value),
        TEST(lambda value: value >= 10.0)
    )
    def warning_very_high_hba1c(self, value):
        self.add_rule_result(
            rule_id="EX_F013",
            condition_id="urgent_medical_attention_pattern",
            weight=8,
            explanation="Very high HbA1c suggests poor long-term glucose control and should be reviewed by a healthcare professional.",
            source="Experta red flag rule: HbA1c >= 10"
        )

    @Rule(
        LabValue(test="fructosamine", value=MATCH.value),
        TEST(lambda value: value > 400)
    )
    def warning_very_high_fructosamine(self, value):
        self.add_rule_result(
            rule_id="EX_F014",
            condition_id="urgent_medical_attention_pattern",
            weight=7,
            explanation="Very high fructosamine may suggest poor short-term glucose control and should be reviewed by a healthcare professional.",
            source="Experta red flag rule: fructosamine > 400"
        )


def run_experta_engine(statuses, patient_values=None, patient_context=None):
    if patient_values is None:
        patient_values = {}

    if patient_context is None:
        patient_context = {}

    engine = MedicalExpertEngine()
    engine.reset()

    if patient_context:
        engine.declare(PatientInfo(
            sex=patient_context.get("sex"),
            age=patient_context.get("age"),
            age_group=patient_context.get("age_group")
        ))

    for test, status in statuses.items():
        engine.declare(LabStatus(
            test=test,
            status=status
        ))

    for test, value in patient_values.items():
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            continue

        engine.declare(LabValue(
            test=test,
            value=numeric_value
        ))

    engine.run()

    return engine.matched_rules