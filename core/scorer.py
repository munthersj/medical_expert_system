def calculate_condition_scores(matched_rules):
    condition_scores = {}
    for rule in matched_rules:
        cid = rule["condition_id"]
        if cid not in condition_scores:
            condition_scores[cid] = {"score":0,"matched_rules":[],"explanations":[],"sources":[]}
        condition_scores[cid]["score"] += rule["weight"]
        condition_scores[cid]["matched_rules"].append(rule["id"])
        condition_scores[cid]["explanations"].append(rule["explanation"])
        src = rule.get("source")
        if src and src not in condition_scores[cid]["sources"]:
            condition_scores[cid]["sources"].append(src)
    return condition_scores

def get_score_level(score, severity_levels):
    for level in severity_levels["score_levels"]:
        if level["min_score"] <= score <= level["max_score"]:
            return {"label":level["label"],"display_name":level["display_name"]}
    return {"label":"unknown","display_name":"Unknown evidence level"}
