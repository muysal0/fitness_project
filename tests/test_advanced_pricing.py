import pytest
from src.app import calculate_final_price

@pytest.mark.parametrize("is_student, occupancy_rate, expected_price", [
    (False, 0.50, 100.0),
    (True,  0.50, 50.0),
    (False, 0.90, 120.0),
    (True,  0.90, 60.0),
])
def test_decision_table_pricing(is_student, occupancy_rate, expected_price):
    base_price = 100.0
    # DÜZELTME: Sona "12:00" ekledik (Peak hour zammı olmasın diye)
    actual_price = calculate_final_price(base_price, is_student, occupancy_rate, "12:00")
    assert actual_price == expected_price