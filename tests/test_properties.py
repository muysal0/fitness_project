import pytest
from hypothesis import given, strategies as st
from src.app import calculate_final_price, calculate_refund

@given(
    base_price=st.floats(min_value=1.0, max_value=1000.0),
    is_student=st.booleans(),
    occupancy_rate=st.floats(min_value=0.0, max_value=1.0)
)
def test_price_properties(base_price, is_student, occupancy_rate):
    final_price = calculate_final_price(base_price, is_student, occupancy_rate)
    
    # 1. Fiyat Pozitif mi?
    assert final_price > 0
    
    # 2. Sınır Kontrolü (Yuvarlama hatası toleransı)
    max_possible = round(base_price * 1.20, 2)
    assert final_price <= max_possible
    
    # 3. Öğrenci Kontrolü
    if is_student:
        standard_price = calculate_final_price(base_price, False, occupancy_rate)
        assert final_price <= standard_price

@given(
    paid_amount=st.floats(min_value=10.0, max_value=500.0),
    hours_until_class=st.integers(min_value=-10, max_value=100)
)
def test_refund_properties(paid_amount, hours_until_class):
    refund = calculate_refund(paid_amount, hours_until_class)
    assert refund <= paid_amount
    assert refund >= 0.0