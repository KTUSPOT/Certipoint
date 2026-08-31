# KTU Activity Point Certificate Analysis System — Person 3 Module

## 📌 Overview & Responsibilities

**Person 3's Module** is responsible for:
1. **Certificate Data Validation**: Verifying that mandatory fields (`student_name`, `activity`, `category`, `level`) exist and that activity categories and levels match registered regulations.
2. **Duplicate Detection**: Preventing double-counting and duplicate submissions using certificate IDs or normalized composite metadata tuples.
3. **KTU Activity Point Calculation**: Mapping verified categories and levels to activity points.
4. **Final Result Generation**: Returning a standardized result dictionary for subsequent pipeline stages (Person 4 / Frontend / Database).

---

## 🚀 How Person 2 Connects to Person 3

Person 2 (Classifier) simply imports and calls `analyse_certificate`:

```python
from person3_validation import analyse_certificate

# Classified certificate dictionary produced by Person 2
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

# Process with Person 3 module
result = analyse_certificate(person2_output)
print(result)
```

---

## 📊 Output Formats

### 1. Valid Certificate
```python
{
    "status": "Valid",
    "student_name": "Jithu",
    "activity": "Blood Donation",
    "category": "Social Service",
    "level": "Participation",
    "points": 2,
    "message": "Certificate successfully analysed"
}
```

### 2. Duplicate Certificate
```python
{
    "status": "Duplicate",
    "points": 0,
    "message": "Certificate already submitted"
}
```

### 3. Validation Failure
```python
{
    "status": "Invalid",
    "points": 0,
    "message": "Validation failed: Missing or empty required field: 'category'"
}
```

---

## ⚙️ Configurable KTU Activity Points Structure

> [!NOTE]
> Point values provided in `DEFAULT_KTU_POINT_RULES` are **sample placeholders** for testing and development and do not claim to be official KTU point values.

You can modify `DEFAULT_KTU_POINT_RULES` in [person3_validation.py](file:///c:/Users/viswa/OneDrive/Desktop/Certipoint/person3_validation.py) or pass custom official rules dynamically:

```python
official_rules = {
    "Technical Event": {
        "National Level Winner": 25,
        "State Level Winner": 15
    }
}

result = analyse_certificate(person2_output, rules=official_rules)
```

---

## 🧪 Running Tests & Examples

### Run Unit Tests
```bash
python -m unittest test_person3.py
```

### Run Integration Example
```bash
python integration_example.py
```
