from flask import Flask, request, jsonify, render_template
from kbs_engine import diagnose, SOURCES

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


def explain(trace):
    """Turn a trace dict into display-ready text. Mirrors print_result()."""
    r = trace["result"]
    lines = []
    if r == "referral":
        symptom, rule_id = trace["emergency_hit"]
        heading = "Immediate Referral Required"
        advice = "Visit the nearest healthcare facility immediately."
        lines.append(f"Rule fired: {rule_id} — IF {symptom} THEN refer_urgent")
        lines.append(f"Source: {SOURCES.get(symptom, 'n/a')}")
        lines.append("Reasoning stopped immediately — emergency rules take priority.")
    elif r in ("malaria", "typhoid"):
        matches = trace["malaria_matches"] if r == "malaria" else trace["typhoid_matches"]
        heading = f"Preliminary Indication: {r.upper()}"
        advice = "Visit a healthcare facility for laboratory confirmation."
        cases = ", ".join(f"{s} ({rid})" for s, rid in trace["case_matches"])
        found = ", ".join(f"{s} ({rid})" for s, rid in matches)
        lines.append(f"Case established via: {cases}")
        lines.append(f"{r.capitalize()}-specific facts matched: {found}")
        lines.append("No conflicting facts for the other disease were present.")
    elif r == "conflicting":
        heading = "Laboratory Investigation Required"
        advice = "Symptoms alone cannot distinguish the two diseases."
        m = ", ".join(f"{s} ({rid})" for s, rid in trace["malaria_matches"])
        t = ", ".join(f"{s} ({rid})" for s, rid in trace["typhoid_matches"])
        lines.append(f"Malaria-specific matches: {m}")
        lines.append(f"Typhoid-specific matches: {t}")
        lines.append("Facts for both diseases were present.")
    elif r == "insufficient_no_case":
        heading = "Insufficient Information"
        advice = "No case-establishing symptoms were reported."
        lines.append("Reasoning stopped at Stage 2 — no plausible case to assess.")
    else:
        heading = "Laboratory Investigation Required"
        advice = "No distinguishing symptoms were confirmed for either disease."
        cases = ", ".join(f"{s} ({rid})" for s, rid in trace["case_matches"])
        lines.append(f"Case established via: {cases}")

    return {"heading": heading, "advice": advice, "result": r,
            "explanation": lines, "stage": trace["stage_reached"]}


@app.route("/diagnose", methods=["POST"])
def api_diagnose():
    data = request.get_json(silent=True) or {}
    symptoms = data.get("symptoms", [])
    trace = diagnose(symptoms)
    return jsonify(explain(trace))


if __name__ == "__main__":
    app.run(debug=True)
