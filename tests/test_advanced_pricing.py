import pytest
from src.app import calculate_final_price

# DECISION TABLE TESTİ
# Tablodaki 4 kuralı buraya "parametre" olarak giriyoruz.
@pytest.mark.parametrize("is_student, occupancy_rate, expected_price", [
    # Kural 1: Standart Üye, Düşük Doluluk -> Fiyat 100
    (False, 0.50, 100.0),
    
    # Kural 2: Öğrenci, Düşük Doluluk -> Fiyat 50 (%50 İndirim)
    (True,  0.50, 50.0),
    
    # Kural 3: Standart Üye, Yüksek Doluluk -> Fiyat 120 (%20 Zam)
    (False, 0.90, 120.0),
    
    # Kural 4: Öğrenci, Yüksek Doluluk -> Fiyat 60 (50 TL üzerinden %20 zam)
    (True,  0.90, 60.0),
])
def test_decision_table_pricing(is_student, occupancy_rate, expected_price):
    # Arrange
    base_price = 100.0
    
    # Act
    actual_price = calculate_final_price(base_price, is_student, occupancy_rate)
    
    # Assert
    assert actual_price == expected_price