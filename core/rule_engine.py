import collections
import collections.abc
if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping
from experta import KnowledgeEngine, Fact, Rule, MATCH

class LabStatus(Fact):
    pass

def condition_matches(statuses, condition):
    test = condition.get("test")
    if test not in statuses:
        return False
    current_status = statuses[test]
    if "status" in condition:
        return current_status == condition["status"]
    if "status_in" in condition:
        return current_status in condition["status_in"]
    return False

def rule_matches(statuses, rule):
    when = rule.get("when", {})
    all_conditions = when.get("all", [])
    any_conditions = when.get("any", [])
    not_conditions = when.get("not", [])
    for condition in all_conditions:
        if not condition_matches(statuses, condition):
            return False
    if any_conditions:
        any_matched_count = sum(1 for condition in any_conditions if condition_matches(statuses, condition))
        min_matched = when.get("min_matched", 1)
        if any_matched_count < min_matched:
            return False
    for condition in not_conditions:
        if condition_matches(statuses, condition):
            return False
    return bool(all_conditions or any_conditions)

class JsonRuleEngine(KnowledgeEngine):
    def __init__(self, statuses, rules):
        super().__init__()
        self.statuses = statuses
        self.rules_data = rules
        self.matched_rules = []

    @Rule(LabStatus(test=MATCH.test, status=MATCH.status))
    def activate(self, test, status):
        pass

    def evaluate_json_rules(self):
        seen_ids = set()
        for rule in self.rules_data:
            if not rule.get("active", True):
                continue
            if rule["id"] in seen_ids:
                continue
            if rule_matches(self.statuses, rule):
                seen_ids.add(rule["id"])
                self.matched_rules.append({
                    "id": rule["id"],
                    "condition_id": rule["condition_id"],
                    "weight": rule["weight"],
                    "explanation": rule["explanation"],
                    "source": rule.get("source", "")
                })

def run_rule_engine(statuses, rules):
    engine = JsonRuleEngine(statuses=statuses, rules=rules)
    engine.reset()
    for test, status in statuses.items():
        engine.declare(LabStatus(test=test, status=status))
    engine.run()
    engine.evaluate_json_rules()
    return engine.matched_rules
