"""
test_person3.py
---------------
Unit Test Suite for Person 3 Module (person3_validation.py)
Run with: python -m unittest test_person3.py
"""

import unittest
from person3_validation import (
    validate_data,
    check_duplicate,
    calculate_points,
    analyse_certificate,
    reset_submitted_certificates,
    DEFAULT_KTU_POINT_RULES
)


class TestPerson3Validation(unittest.TestCase):

    def setUp(self):
        """Reset submitted certificates state before each test."""
        reset_submitted_certificates()

    def test_valid_certificate_analysis(self):
        """Test processing a normal valid certificate from Person 2."""
        person2_output = {
            "student_name": "Jithu",
            "activity": "Blood Donation",
            "organization": "NSS Unit",
            "date": "15-08-2026",
            "certificate_id": "NSS12345",
            "category": "Social Service",
            "level": "Participation",
            "confidence": 0.95
        }

        result = analyse_certificate(person2_output)

        self.assertEqual(result["status"], "Valid")
        self.assertEqual(result["student_name"], "Jithu")
        self.assertEqual(result["activity"], "Blood Donation")
        self.assertEqual(result["category"], "Social Service")
        self.assertEqual(result["level"], "Participation")
        self.assertEqual(result["points"], 2)
        self.assertEqual(result["message"], "Certificate successfully analysed")

    def test_duplicate_certificate_detection(self):
        """Test that submitting the same certificate twice yields a Duplicate status."""
        person2_output = {
            "student_name": "Jithu",
            "activity": "Blood Donation",
            "organization": "NSS Unit",
            "date": "15-08-2026",
            "certificate_id": "NSS12345",
            "category": "Social Service",
            "level": "Participation",
            "confidence": 0.95
        }

        first_run = analyse_certificate(person2_output)
        self.assertEqual(first_run["status"], "Valid")

        second_run = analyse_certificate(person2_output)
        self.assertEqual(second_run["status"], "Duplicate")
        self.assertEqual(second_run["points"], 0)
        self.assertEqual(second_run["message"], "Certificate already submitted")

    def test_duplicate_by_certificate_id(self):
        """Test duplicate detection matching by explicit certificate_id."""
        cert1 = {
            "student_name": "Jithu",
            "activity": "Blood Donation Camp",
            "category": "Social Service",
            "level": "Participation",
            "certificate_id": "CERT-999"
        }
        cert2 = {
            "student_name": "Jithu",
            "activity": "Blood Donation Event",  # Slight string difference in activity
            "category": "Social Service",
            "level": "Participation",
            "certificate_id": "CERT-999"        # Same unique certificate ID
        }

        self.assertEqual(analyse_certificate(cert1)["status"], "Valid")
        self.assertEqual(analyse_certificate(cert2)["status"], "Duplicate")

    def test_duplicate_without_certificate_id(self):
        """Test duplicate detection fallback using composite tuple signature."""
        cert1 = {
            "student_name": "Anjali",
            "activity": "Paper Presentation",
            "category": "Technical Event",
            "level": "Winner"
        }
        cert2 = {
            "student_name": "Anjali",
            "activity": "Paper Presentation",
            "category": "Technical Event",
            "level": "Winner"
        }

        self.assertEqual(analyse_certificate(cert1)["status"], "Valid")
        self.assertEqual(analyse_certificate(cert2)["status"], "Duplicate")

    def test_missing_required_fields(self):
        """Test validation failure when mandatory fields are omitted or blank."""
        invalid_cases = [
            {"activity": "Blood Donation", "category": "Social Service", "level": "Participation"},  # Missing student_name
            {"student_name": "Jithu", "category": "Social Service", "level": "Participation"},     # Missing activity
            {"student_name": "Jithu", "activity": "Blood Donation", "level": "Participation"},     # Missing category
            {"student_name": "Jithu", "activity": "Blood Donation", "category": "Social Service"}, # Missing level
            {"student_name": "  ", "activity": "Blood Donation", "category": "Social Service", "level": "Participation"}, # Whitespace
        ]

        for case in invalid_cases:
            result = analyse_certificate(case)
            self.assertEqual(result["status"], "Invalid")
            self.assertEqual(result["points"], 0)
            self.assertTrue(result["message"].startswith("Validation failed:"))

    def test_invalid_category_or_level(self):
        """Test validation failure for unknown activity category or level."""
        bad_category = {
            "student_name": "Jithu",
            "activity": "Gaming",
            "category": "Esports",  # Category not in rules
            "level": "Participation"
        }
        res_cat = analyse_certificate(bad_category)
        self.assertEqual(res_cat["status"], "Invalid")

        bad_level = {
            "student_name": "Jithu",
            "activity": "Blood Donation",
            "category": "Social Service",
            "level": "Universe Level"  # Level not in rules for Social Service
        }
        res_lvl = analyse_certificate(bad_level)
        self.assertEqual(res_lvl["status"], "Invalid")

    def test_non_dict_input(self):
        """Test graceful handling of non-dict inputs."""
        res_none = analyse_certificate(None)
        self.assertEqual(res_none["status"], "Invalid")
        self.assertEqual(res_none["points"], 0)

        res_str = analyse_certificate("Invalid input string")
        self.assertEqual(res_str["status"], "Invalid")
        self.assertEqual(res_str["points"], 0)

    def test_calculate_points(self):
        """Test point calculation logic directly."""
        pts1 = calculate_points("Social Service", "Participation")
        self.assertEqual(pts1, 2)

        pts2 = calculate_points("Sports", "National Level")
        self.assertEqual(pts2, 40)

        pts_invalid = calculate_points("NonExistent", "Level")
        self.assertEqual(pts_invalid, 0)

    def test_custom_ktu_rules_injection(self):
        """Test overriding default rules with official/custom KTU point rules."""
        custom_rules = {
            "Robotics": {
                "International Winner": 100
            }
        }
        cert_data = {
            "student_name": "Jithu",
            "activity": "Robofest",
            "category": "Robotics",
            "level": "International Winner"
        }

        result = analyse_certificate(cert_data, rules=custom_rules)
        self.assertEqual(result["status"], "Valid")
        self.assertEqual(result["points"], 100)


if __name__ == "__main__":
    unittest.main()
