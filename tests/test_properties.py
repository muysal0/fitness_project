import pytest
from hypothesis import given, strategies as st
from src.app import calculate_final_price, calculate_refund

# PROPERTY 1: FİYATLANDIRMA KURALLARI
# Senaryo: Taban fiyat 1 ile 1000 arasında, doluluk 0 ile 1 arasında değişsin.
@given(
    base_price=st.floats(min_value=1.0, max_value=1000.0),
    is_student=st.booleans(),
    occupancy_rate=st.floats(min_value=0.0, max_value=1.0)
)
def test_price_properties(base_price, is_student, occupancy_rate):
    """
    Özellik (Invariant):
    1. Fiyat asla 0 veya negatif olamaz.
    2. Fiyat ASLA (Taban Fiyat * 1.2)'den büyük olamaz. (Yuvarlama hatası düzeltildi)
    3. Öğrenci fiyatı <= Standart fiyat.
    """
    final_price = calculate_final_price(base_price, is_student, occupancy_rate)
    
    # 1. Fiyat Pozitif mi?
    assert final_price > 0
    
    # 2. Maksimum Sınır Kontrolü (DÜZELTİLDİ)
    # Uygulamada round(x, 2) kullandığımız için, karşılaştırma limitini de yuvarlıyoruz.
    # Veya matematiksel hassasiyet payı (tolerance) bırakıyoruz.
    max_possible_price = round(base_price * 1.20, 2)
    assert final_price <= max_possible_price
    
    # 3. Öğrenci Kontrolü
    if is_student:
        standard_price = calculate_final_price(base_price, False, occupancy_rate)
        assert final_price <= standard_price

# PROPERTY 2: İADE (REFUND) KURALLARI
# Senaryo: Ödenen miktar pozitif, kalan saat -10 ile 100 arasında değişsin.
@given(
    paid_amount=st.floats(min_value=10.0, max_value=500.0),
    hours_until_class=st.integers(min_value=-10, max_value=100)
)
def test_refund_properties(paid_amount, hours_until_class):
    """
    Özellik (Invariant):
    1. İade miktarı asla ödenen miktardan fazla olamaz.
    2. İade miktarı asla negatif olamaz.
    """
    refund = calculate_refund(paid_amount, hours_until_class)
    
    # 1. Sınır Kontrolü
    assert refund <= paid_amount
    
    # 2. Negatiflik Kontrolü
    assert refund >= 0.0