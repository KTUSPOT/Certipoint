"""
integration_example.py
----------------------
Demonstration of how Person 2 connects to Person 3 and passes structured 
classified certificate data for validation, duplicate detection, and KTU point calculation.
"""

import json
from person3_validation import analyse_certificate, reset_submitted_certificates


def simulate_person_2_classifier(raw_ocr_text: str) -> dict:
    """
    Simulates Person 2's Activity Classifier module.
    Receives text from Person 1 (OCR) and converts it into structured output.
    """
    print(f"[Person 2] Classifying raw OCR text:\n  \"{raw_ocr_text[:65]}...\"")
    
    return {
        "student_name": "Jithu",
        "activity": "Blood Donation",
        "organization": "NSS Unit",
        "date": "15-08-2026",
        "certificate_id": "NSS12345",
        "category": "Social Service",
        "level": "Participation",
        "confidence": 0.95
    }


def main():
    # Clear in-memory duplicate records for clean demonstration
    reset_submitted_certificates()

    print("=" * 60)
    print("KTU Certificate Analysis Pipeline: Person 2 -> Person 3")
    print("=" * 60)

    # -------------------------------------------------------------
    # Scenario 1: Standard Valid Certificate Submission
    # -------------------------------------------------------------
    print("\n--- Scenario 1: Valid Certificate Submission ---")
    ocr_sample = "Certificate of Appreciation awarded to Jithu for Blood Donation conducted by NSS Unit on 15-08-2026. Ref: NSS12345"
    person2_output = simulate_person_2_classifier(ocr_sample)

    print("\n[Person 2 Output Data]:")
    print(json.dumps(person2_output, indent=4))

    print("\n[Person 3] Calling analyse_certificate(person2_output)...")
    person3_result = analyse_certificate(person2_output)

    print("\n[Person 3 Output Result (Passed to Person 4 / Frontend / Database)]:")
    print(json.dumps(person3_result, indent=4))

    # -------------------------------------------------------------
    # Scenario 2: Duplicate Certificate Submission Detection
    # -------------------------------------------------------------
    print("\n--- Scenario 2: Duplicate Certificate Detection ---")
    print("[Simulation] Re-submitting the exact same certificate data...")
    duplicate_result = analyse_certificate(person2_output)

    print("\n[Person 3 Duplicate Detection Result]:")
    print(json.dumps(duplicate_result, indent=4))

    # -------------------------------------------------------------
    # Scenario 3: Validation Failure (Missing Required Field)
    # -------------------------------------------------------------
    print("\n--- Scenario 3: Missing Required Field Handling ---")
    invalid_person2_output = {
        "student_name": "Jithu",
        "activity": "Paper Presentation",
        # "category" field intentionally omitted!
        "level": "Winner"
    }
    print("[Person 2 Output Data with missing category]:")
    print(json.dumps(invalid_person2_output, indent=4))

    invalid_result = analyse_certificate(invalid_person2_output)
    print("\n[Person 3 Validation Error Result]:")
    print(json.dumps(invalid_result, indent=4))

    # -------------------------------------------------------------
    # Scenario 4: Custom KTU Rules Injection (When Official Rules are Loaded)
    # -------------------------------------------------------------
    print("\n--- Scenario 4: Custom KTU Rules Injection ---")
    official_ktu_rules = {
        "Technical Event": {
            "National Level Winner": 25,
            "State Level Winner": 15
        }
    }
    custom_cert = {
        "student_name": "Rahul",
        "activity": "Hackathon 2026",
        "category": "Technical Event",
        "level": "National Level Winner",
        "certificate_id": "HACK-9921"
    }
    print(f"[Person 2 Output Data]:\n{json.dumps(custom_cert, indent=4)}")
    custom_result = analyse_certificate(custom_cert, rules=official_ktu_rules)
    print(f"\n[Person 3 Result with Custom Rules]:\n{json.dumps(custom_result, indent=4)}")


if __name__ == "__main__":
    main()
