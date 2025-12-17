import pytest
from src.membership import Member
from src.fitness_class import FitnessClass
from src.pricing_service import calculate_price

# DECISION TABLE (KARAR TABLOSU)
# Taban Fiyat: 100.0 TL
# Kurallar:
# 1. Standart Üye: İndirim yok.
# 2. Öğrenci: %50 İndirim.
# 3. Doluluk > %80: %20 Zam (Surge).

@pytest.mark.parametrize("membership_type, occupancy_rate, expected_price", [
    # Senaryo 1: Standart üye, sınıf boş (%10) -> Fiyat değişmez (100.0)
    ("standard", 0.10, 100.0), 
    
    # Senaryo 2: Öğrenci, sınıf boş (%10) -> %50 İndirim (100 * 0.5 = 50.0)
    ("student",  0.10, 50.0),  
    
    # Senaryo 3: Standart, sınıf dolu (%90) -> %20 Zam (100 * 1.2 = 120.0)
    ("standard", 0.90, 120.0), 
    
    # Senaryo 4: Öğrenci, sınıf dolu (%90) -> Hem zam hem indirim
    # Matematik: 100 TL * 1.20 (Zam) = 120 TL. 
    # Sonra %50 Öğrenci indirimi: 120 * 0.5 = 60 TL.
    ("student",  0.90, 60.0),  
])
def test_dynamic_pricing_decision_table(membership_type, occupancy_rate, expected_price):
    # Arrange
    f_class = FitnessClass("Zumba", "Test Hoca", 10, "2025-01-01", base_price=100.0)
    
    # Doluluk oranına göre rezervasyon listesini doldur
    current_count = int(10 * occupancy_rate)
    f_class.reservations = [i for i in range(current_count)] 
    
    member = Member(1, "Test Uye", membership_type)

    # Act
    actual_price = calculate_price(f_class, member)

    # Assert
    assert actual_price == pytest.approx(expected_price, 0.01)