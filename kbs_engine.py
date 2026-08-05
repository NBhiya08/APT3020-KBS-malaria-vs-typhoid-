"""
Medical Diagnosis Expert System — Malaria vs Typhoid Fever
Inference engine implemented with kanren (Python logic programming).

Rebuilt to match the 3-stage rule priority documented in Sections 2 and 3
of the project report (Emergency > Case-Establishing > Distinguishing),
and to use the same fact IDs, rule IDs and reasoning logic as the web
interface described in Section 5.
"""

from kanren import Relation, facts, run, var

# ---------------------------------------------------------------------
# KNOWLEDGE BASE
# Facts and rule IDs transcribed from Section 2.2 (Emergency Facts,
# Case-Establishing Facts, Distinguishing Facts tables).
# ---------------------------------------------------------------------

# Stage 1 — Emergency Facts (R-EMG-01 .. R-EMG-11)
emergency = Relation()
facts(emergency,
      ("impaired_consciousness", "R-EMG-01"),
      ("too_weak",               "R-EMG-02"),
      ("seizures",                "R-EMG-03"),
      ("rapid_breathing",         "R-EMG-04"),
      ("yellow_skin",             "R-EMG-05"),
      ("bleeding",                "R-EMG-06"),
      ("cold_extremities",        "R-EMG-07"),
      ("severe_abdominal_pain",   "R-EMG-08"),
      ("swollen_abdomen",         "R-EMG-09"),
      ("persistent_vomiting",     "R-EMG-10"),
      ("severe_diarrhoea",        "R-EMG-11"))

# Stage 2 — Case-Establishing Facts (R-CASE-01 .. R-CASE-05)
case_establishing = Relation()
facts(case_establishing,
      ("fever",             "R-CASE-01"),
      ("headache",           "R-CASE-02"),
      ("fatigue_weakness",   "R-CASE-03"),
      ("general_malaise",    "R-CASE-04"),
      ("loss_of_appetite",   "R-CASE-05"))

# Stage 3 — Distinguishing Facts (R-DIST-01 .. R-DIST-08)
distinguishing = Relation()
facts(distinguishing,
      ("chills",                "R-DIST-01", "malaria"),
      ("sweating_after_fever",   "R-DIST-02", "malaria"),
      ("intermittent_fever",     "R-DIST-03", "malaria"),
      ("abdominal_pain",         "R-DIST-04", "typhoid"),
      ("constipation_adult",     "R-DIST-05", "typhoid"),
      ("diarrhoea_child",        "R-DIST-06", "typhoid"),
      ("rose_spots",             "R-DIST-07", "typhoid"),
      ("dry_cough_early",        "R-DIST-08", "typhoid"))

# Source citations for the explanation facility (Section 2.2 "Source" columns)
SOURCES = {
    "impaired_consciousness": "WHO Malaria / Typhoid",
    "too_weak": "WHO Malaria",
    "seizures": "WHO Malaria",
    "rapid_breathing": "WHO Malaria",
    "yellow_skin": "WHO Malaria",
    "bleeding": "WHO Malaria / Typhoid",
    "cold_extremities": "WHO Malaria",
    "severe_abdominal_pain": "WHO Typhoid",
    "swollen_abdomen": "WHO Typhoid",
    "persistent_vomiting": "WHO Typhoid",
    "severe_diarrhoea": "WHO Typhoid",
    "fever": "WHO Malaria, WHO Typhoid",
    "headache": "WHO Malaria, WHO Typhoid",
    "fatigue_weakness": "WHO Malaria, WHO Typhoid",
    "general_malaise": "WHO Malaria, WHO Typhoid",
    "loss_of_appetite": "WHO Typhoid",
    "chills": "WHO Malaria",
    "sweating_after_fever": "WHO Malaria",
    "intermittent_fever": "WHO Malaria",
    "abdominal_pain": "WHO Typhoid",
    "constipation_adult": "WHO Typhoid",
    "diarrhoea_child": "WHO Typhoid",
    "rose_spots": "WHO Typhoid",
    "dry_cough_early": "WHO Typhoid",
}


# ---------------------------------------------------------------------
# INFERENCE ENGINE
# Forward chaining over the three stages, in the priority order fixed
# by Section 3.3: Emergency > Case-Establishing > Distinguishing.
# ---------------------------------------------------------------------

def check_emergency(symptom):
    """Return the rule ID if `symptom` matches an emergency fact, else None."""
    rid = var()
    result = run(0, rid, emergency(symptom, rid))
    return result[0] if result else None


def check_case_establishing(symptom):
    """Return the rule ID if `symptom` matches a case-establishing fact, else None."""
    rid = var()
    result = run(0, rid, case_establishing(symptom, rid))
    return result[0] if result else None


def check_distinguishing(symptom):
    """Return (rule_id, disease) if `symptom` matches a distinguishing fact, else None."""
    rid, disease = var(), var()
    result = run(0, (rid, disease), distinguishing(symptom, rid, disease))
    return result[0] if result else None


def diagnose(symptoms):
    """
    Run the full 3-stage reasoning cycle over a list of asserted symptoms
    and return a trace dict describing the outcome, mirroring the logic
    implemented in the web interface (Section 5.2).
    """
    trace = {"stage_reached": None, "emergency_hit": None,
             "case_matches": [], "malaria_matches": [], "typhoid_matches": [],
             "result": None}

    # Stage 1 — Emergency
    for symptom in symptoms:
        rule_id = check_emergency(symptom)
        if rule_id:
            trace["stage_reached"] = "Emergency"
            trace["emergency_hit"] = (symptom, rule_id)
            trace["result"] = "referral"
            return trace  # emergency rules always short-circuit

    # Stage 2 — Case-Establishing
    for symptom in symptoms:
        rule_id = check_case_establishing(symptom)
        if rule_id:
            trace["case_matches"].append((symptom, rule_id))

    if not trace["case_matches"]:
        trace["stage_reached"] = "Case-Establishing"
        trace["result"] = "insufficient_no_case"
        return trace

    # Stage 3 — Distinguishing (only reached once a case is established)
    trace["stage_reached"] = "Distinguishing"
    for symptom in symptoms:
        match = check_distinguishing(symptom)
        if match:
            rule_id, disease = match
            if disease == "malaria":
                trace["malaria_matches"].append((symptom, rule_id))
            else:
                trace["typhoid_matches"].append((symptom, rule_id))

    m, t = trace["malaria_matches"], trace["typhoid_matches"]
    if m and not t:
        trace["result"] = "malaria"
    elif t and not m:
        trace["result"] = "typhoid"
    elif m and t:
        trace["result"] = "conflicting"
    else:
        trace["result"] = "insufficient_no_distinguishing"
    return trace


# ---------------------------------------------------------------------
# EXPLANATION FACILITY (console output)
# ---------------------------------------------------------------------

def print_result(trace):
    print("\nRESULT")
    if trace["result"] == "referral":
        symptom, rule_id = trace["emergency_hit"]
        print("Immediate Referral Required")
        print("Recommendation: Visit the nearest healthcare facility immediately.")
        print("Explanation:")
        print(f"  Rule fired: {rule_id} — IF {symptom} THEN refer_urgent")
        print(f"  Source: {SOURCES.get(symptom, 'n/a')}")
        print("  Reasoning stopped immediately — emergency rules always take priority.")

    elif trace["result"] == "insufficient_no_case":
        print("Laboratory Investigation Required")
        print("Explanation:")
        print("  No case-establishing facts matched — insufficient evidence to proceed.")

    elif trace["result"] in ("malaria", "typhoid"):
        disease = trace["result"]
        matches = trace["malaria_matches"] if disease == "malaria" else trace["typhoid_matches"]
        print(f"Preliminary Diagnosis: {disease.upper()}")
        print("Recommendation: Visit a healthcare facility for laboratory confirmation.")
        print("Explanation:")
        case_ids = ", ".join(f"{s} ({r})" for s, r in trace["case_matches"])
        match_ids = ", ".join(f"{s} ({r})" for s, r in matches)
        print(f"  Case established via: {case_ids}")
        print(f"  {disease.capitalize()}-specific facts matched: {match_ids}")
        print(f"  No conflicting facts for the other disease were present.")

    elif trace["result"] == "conflicting":
        print("Laboratory Investigation Required (conflicting evidence)")
        print("Explanation:")
        m = ", ".join(f"{s} ({r})" for s, r in trace["malaria_matches"])
        t = ", ".join(f"{s} ({r})" for s, r in trace["typhoid_matches"])
        print(f"  Malaria-specific matches: {m}")
        print(f"  Typhoid-specific matches: {t}")
        print("  Facts for both diseases were present — symptoms alone cannot distinguish them.")

    else:  # insufficient_no_distinguishing
        print("Laboratory Investigation Required")
        print("Explanation:")
        case_ids = ", ".join(f"{s} ({r})" for s, r in trace["case_matches"])
        print(f"  Case established via: {case_ids}")
        print("  No distinguishing facts were confirmed for either disease.")

    print(f"\nStage reached: {trace['stage_reached']}")


# ---------------------------------------------------------------------
# CONSOLE INTERFACE
# ---------------------------------------------------------------------

def run_interview():
    print("Medical Diagnosis Expert System")
    print("--------------------------------")
    print("Enter symptoms one at a time (use the fact IDs from the report).")
    print("Type 'done' when finished.\n")

    symptoms = []
    while True:
        symptom = input("Symptom: ").strip()
        if symptom == "done":
            break
        symptoms.append(symptom)

    trace = diagnose(symptoms)
    print_result(trace)


if __name__ == "__main__":
    run_interview()
