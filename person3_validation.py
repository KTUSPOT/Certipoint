"""
person3_validation.py
---------------------
KTU Activity Point Certificate Analysis System - Person 3 Module

Responsibilities:
1. Certificate Data Validation: Verifies required fields and activity categories/levels.
2. Duplicate Detection: Prevents re-submission of identical certificates/activities.
3. KTU Activity Point Calculation: Maps activity category and level to points.
4. Final Structured Result Generation: Produces standardized dictionary outputs.

Integration Usage (Person 2 -> Person 3):
    from person3_validation import analyse_certificate

    result = analyse_certificate(person2_output)
"""

from typing import Dict, Any, Set, Tuple, Optional, Union

# ==============================================================================
# CONFIGURABLE KTU POINT RULES (SAMPLE PLACEHOLDER RULES)
# ==============================================================================
# IMPORTANT DISCLAIMER:
# The point values below are SAMPLE PLACEHOLDERS for development and testing.
# They do NOT claim to be official APJ Abdul Kalam Technological University (KTU) rules.
# Official KTU regulations can be inserted here or passed dynamically to
# analyse_certificate(..., rules=custom_rules) without altering module logic.
# ==============================================================================

DEFAULT_KTU_POINT_RULES: Dict[str, Dict[str, int]] = {
    "Social Service": {
        "Participation": 2,
        "Organizer": 5,
        "State Level": 10,
        "National Level": 20
    },
    "Sports": {
        "Participation": 2,
        "College Level": 5,
        "Zonal Level": 10,
        "State Level": 20,
        "National Level": 40
    },
    "NSS / NCC": {
        "Volunteer": 10,
        "Camp": 15,
        "C-Certificate": 40
    },
    "Technical Event": {
        "Participation": 3,
        "Paper Presentation": 8,
        "Winner": 10,
        "National Level": 20
    },
    "Cultural": {
        "Participation": 2,
        "College Level": 5,
        "State Level": 15,
        "National Level": 30
    },
    "Leadership / Student Governance": {
        "Member": 5,
        "Co-ordinator": 10,
        "Lead": 15
    }
}

# In-memory store for duplicate detection across certificate submissions
# Stores certificate ID strings or composite metadata tuples
SUBMITTED_CERTIFICATES: Set[Union[str, Tuple[str, str, str, str]]] = set()


def get_certificate_signature(data: Dict[str, Any]) -> Union[str, Tuple[str, str, str, str]]:
    """
    Generates a unique signature for duplicate checking.
    
    If 'certificate_id' is present and non-empty, uses the normalized certificate ID.
    Otherwise, generates a composite tuple: (student_name, activity, category, level).
    """
    cert_id = str(data.get("certificate_id", "")).strip() if data.get("certificate_id") is not None else ""
    if cert_id:
        return f"ID:{cert_id.upper()}"
    
    student_name = str(data.get("student_name", "")).strip().lower()
    activity = str(data.get("activity", "")).strip().lower()
    category = str(data.get("category", "")).strip().lower()
    level = str(data.get("level", "")).strip().lower()
    
    return (student_name, activity, category, level)


def validate_data(
    data: Dict[str, Any], 
    rules: Dict[str, Dict[str, int]] = DEFAULT_KTU_POINT_RULES
) -> Tuple[bool, str]:
    """
    Validates that the input dictionary from Person 2 contains all required fields 
    and that the category and level are recognized within the rules configuration.

    Args:
        data (dict): Certificate data received from Person 2.
        rules (dict): Point rules dictionary against which to validate categories and levels.

    Returns:
        Tuple[bool, str]: (is_valid, validation_message)
    """
    if not isinstance(data, dict):
        return False, "Input data must be a dictionary"

    required_fields = ["student_name", "activity", "category", "level"]
    for field in required_fields:
        val = data.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            return False, f"Missing or empty required field: '{field}'"

    category = str(data.get("category")).strip()
    if category not in rules:
        valid_cats = ", ".join(list(rules.keys()))
        return False, f"Invalid activity category '{category}'. Valid categories are: {valid_cats}"

    level = str(data.get("level")).strip()
    if level not in rules[category]:
        valid_levels = ", ".join(list(rules[category].keys()))
        return False, f"Invalid level '{level}' for category '{category}'. Valid levels are: {valid_levels}"

    return True, "Data is valid"


def check_duplicate(
    data: Dict[str, Any], 
    submitted_records: Optional[Set[Any]] = None
) -> bool:
    """
    Checks whether the certificate or activity submission already exists in submitted records.

    Args:
        data (dict): Certificate data received from Person 2.
        submitted_records (set, optional): Set of existing certificate signatures. 
                                           Defaults to SUBMITTED_CERTIFICATES.

    Returns:
        bool: True if duplicate exists, False otherwise.
    """
    records = SUBMITTED_CERTIFICATES if submitted_records is None else submitted_records
    signature = get_certificate_signature(data)
    return signature in records


def calculate_points(
    category: str, 
    level: str, 
    rules: Dict[str, Dict[str, int]] = DEFAULT_KTU_POINT_RULES
) -> int:
    """
    Matches category and level against the rules configuration to calculate activity points.

    Args:
        category (str): The activity category (e.g. 'Social Service').
        level (str): The activity level (e.g. 'Participation').
        rules (dict): Point rules mapping categories and levels to integer points.

    Returns:
        int: Calculated activity points, or 0 if category/level not found.
    """
    if not isinstance(category, str) or not isinstance(level, str) or not isinstance(rules, dict):
        return 0

    cat_rules = rules.get(category.strip())
    if not cat_rules or not isinstance(cat_rules, dict):
        return 0

    return cat_rules.get(level.strip(), 0)


def analyse_certificate(
    data: Dict[str, Any], 
    submitted_records: Optional[Set[Any]] = None, 
    rules: Dict[str, Dict[str, int]] = DEFAULT_KTU_POINT_RULES,
    auto_record: bool = True
) -> Dict[str, Any]:
    """
    Primary processing function to analyze certificate data received from Person 2.
    Performs validation, duplicate detection, and KTU activity point calculation.

    Args:
        data (dict): Structured certificate classification data from Person 2.
        submitted_records (set, optional): Set of existing certificate signatures for duplicate checking.
        rules (dict, optional): Custom point rules dictionary.
        auto_record (bool): If True and certificate is valid, records certificate signature
                            to prevent future duplicate submissions.

    Returns:
        dict: Structured result containing status, details, points, and message.
    """
    try:
        records = SUBMITTED_CERTIFICATES if submitted_records is None else submitted_records

        # Step 1: Validate input data
        is_valid, validation_msg = validate_data(data, rules=rules)
        if not is_valid:
            return {
                "status": "Invalid",
                "points": 0,
                "message": f"Validation failed: {validation_msg}"
            }

        # Step 2: Check for duplicate submission
        if check_duplicate(data, submitted_records=records):
            return {
                "status": "Duplicate",
                "points": 0,
                "message": "Certificate already submitted"
            }

        # Step 3: Calculate activity points
        category = str(data["category"]).strip()
        level = str(data["level"]).strip()
        points = calculate_points(category, level, rules=rules)

        # Step 4: Record signature if auto_record enabled
        if auto_record:
            signature = get_certificate_signature(data)
            records.add(signature)

        # Step 5: Format and return final result
        return {
            "status": "Valid",
            "student_name": str(data["student_name"]).strip(),
            "activity": str(data["activity"]).strip(),
            "category": category,
            "level": level,
            "points": points,
            "message": "Certificate successfully analysed"
        }
    except Exception as e:
        return {
            "status": "Invalid",
            "points": 0,
            "message": f"Unexpected error during processing: {str(e)}"
        }


def reset_submitted_certificates():
    """Helper function to clear in-memory duplicate records (useful for testing and resets)."""
    SUBMITTED_CERTIFICATES.clear()
