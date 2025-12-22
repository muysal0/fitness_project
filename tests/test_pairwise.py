import pytest
from src.app import calculate_final_price

@pytest.mark.parametrize("membership, class_type, occupancy, time, expected_price", [
    ("standard", "yoga", 0.5, "morning", 100.0),
    ("standard", "spinning", 0.9, "evening", 180.0),
    ("student", "yoga", 0.9, "evening", 60.0),
    ("student", "spinning", 0.5, "morning", 75.0),
    ("premium", "yoga", 0.9, "morning", 120.0),
    ("premium", "spinning", 0.5, "evening", 150.0),
])
def test_pairwise_combinations(membership, class_type, occupancy, time, expected_price):
    base_price = 100.0 if class_type == "yoga" else 150.0
    is_student = (membership == "student")
    actual_price = calculate_final_price(base_price, is_student, occupancy)
    assert actual_price == expected_price