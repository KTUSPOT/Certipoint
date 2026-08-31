"""
app.py
------
Certipoint - KTU Activity Point Certificate Analysis System Web Application
Flask backend serving the web dashboard and REST API for Person 3 validation.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
from typing import Dict, Any

from person3_validation import (
    analyse_certificate,
    validate_data,
    check_duplicate,
    calculate_points,
    reset_submitted_certificates,
    DEFAULT_KTU_POINT_RULES,
    SUBMITTED_CERTIFICATES,
    get_certificate_signature
)

app = Flask(__name__, static_folder="static", template_folder="templates")

# In-memory storage for active session
active_rules = json.loads(json.dumps(DEFAULT_KTU_POINT_RULES))
processed_records = []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyse", methods=["POST"])
def api_analyse():
    """Endpoint to analyse certificate data from Person 2."""
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"status": "Invalid", "points": 0, "message": "No JSON payload provided"}), 400

        # Run Person 3 analysis with active configurable rules
        result = analyse_certificate(data, rules=active_rules, auto_record=True)
        
        # Log record if valid or duplicate for history tracking
        record_entry = {
            "input": data,
            "result": result,
            "timestamp": data.get("date", "Today")
        }
        processed_records.insert(0, record_entry)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "Invalid",
            "points": 0,
            "message": f"Server processing error: {str(e)}"
        }), 500


@app.route("/api/rules", methods=["GET", "POST"])
def api_rules():
    """Get or update active KTU activity point rules."""
    global active_rules
    if request.method == "POST":
        try:
            new_rules = request.get_json(force=True)
            if not isinstance(new_rules, dict):
                return jsonify({"error": "Rules must be a JSON object"}), 400
            active_rules = new_rules
            return jsonify({"status": "success", "message": "Rules updated successfully", "rules": active_rules})
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    return jsonify({
        "rules": active_rules,
        "is_default": active_rules == DEFAULT_KTU_POINT_RULES
    })


@app.route("/api/rules/reset", methods=["POST"])
def api_rules_reset():
    """Reset rules to default sample rules."""
    global active_rules
    active_rules = json.loads(json.dumps(DEFAULT_KTU_POINT_RULES))
    return jsonify({"status": "success", "message": "Rules reset to default", "rules": active_rules})


@app.route("/api/history", methods=["GET"])
def api_history():
    """Get processed certificates and calculated student point summary."""
    student_summary = {}
    for entry in processed_records:
        res = entry.get("result", {})
        if res.get("status") == "Valid":
            name = res.get("student_name", "Unknown")
            pts = res.get("points", 0)
            cat = res.get("category", "Other")
            
            if name not in student_summary:
                student_summary[name] = {
                    "total_points": 0,
                    "valid_certs": 0,
                    "categories": {}
                }
            student_summary[name]["total_points"] += pts
            student_summary[name]["valid_certs"] += 1
            student_summary[name]["categories"][cat] = student_summary[name]["categories"].get(cat, 0) + pts

    return jsonify({
        "records": processed_records,
        "student_summary": student_summary,
        "duplicate_count": len(SUBMITTED_CERTIFICATES)
    })


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Reset duplicate records and history."""
    reset_submitted_certificates()
    processed_records.clear()
    return jsonify({"status": "success", "message": "Duplicate database and history cleared."})


@app.route("/api/simulate-p2", methods=["POST"])
def api_simulate_p2():
    """
    Simulates Person 2 NLP classification pipeline based on preset activity selections
    or raw OCR input text, then forwards to Person 3.
    """
    data = request.get_json(force=True) or {}
    preset_type = data.get("preset", "blood_donation")

    presets = {
        "blood_donation": {
            "student_name": data.get("student_name") or "Jithu",
            "activity": "Blood Donation",
            "organization": "NSS Unit",
            "date": "15-08-2026",
            "certificate_id": "NSS12345",
            "category": "Social Service",
            "level": "Participation",
            "confidence": 0.95
        },
        "nss_camp": {
            "student_name": data.get("student_name") or "Jithu",
            "activity": "7-Day Special Camp",
            "organization": "NSS Cell",
            "date": "20-07-2026",
            "certificate_id": "NSS-CAMP-401",
            "category": "NSS / NCC",
            "level": "Camp",
            "confidence": 0.98
        },
        "hackathon_winner": {
            "student_name": data.get("student_name") or "Anjali",
            "activity": "National AI Hackathon",
            "organization": "IEEE Kerala Section",
            "date": "10-06-2026",
            "certificate_id": "IEEE-HACK-88",
            "category": "Technical Event",
            "level": "Winner",
            "confidence": 0.92
        },
        "sports_national": {
            "student_name": data.get("student_name") or "Rahul",
            "activity": "Inter-University Badminton",
            "organization": "KTU Sports Council",
            "date": "05-04-2026",
            "certificate_id": "SPORTS-KTU-102",
            "category": "Sports",
            "level": "National Level",
            "confidence": 0.96
        },
        "paper_presentation": {
            "student_name": data.get("student_name") or "Jithu",
            "activity": "International Tech Conference",
            "organization": "CSI Student Chapter",
            "date": "12-05-2026",
            "certificate_id": "CSI-PAPER-331",
            "category": "Technical Event",
            "level": "Paper Presentation",
            "confidence": 0.91
        },
        "cultural_state": {
            "student_name": data.get("student_name") or "Sneha",
            "activity": "KTU Arts Fest - Classical Dance",
            "organization": "KTU Union",
            "date": "28-02-2026",
            "certificate_id": "KTU-ARTS-707",
            "category": "Cultural",
            "level": "State Level",
            "confidence": 0.94
        }
    }

    person2_output = presets.get(preset_type, presets["blood_donation"])
    # Allow user override fields
    for k, v in data.items():
        if k in person2_output and v:
            person2_output[k] = v

    # Pass to Person 3
    person3_result = analyse_certificate(person2_output, rules=active_rules, auto_record=True)
    processed_records.insert(0, {
        "input": person2_output,
        "result": person3_result,
        "timestamp": person2_output.get("date", "Today")
    })

    return jsonify({
        "person2_output": person2_output,
        "person3_result": person3_result
    })


if __name__ == "__main__":
    # Run the server on port 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
