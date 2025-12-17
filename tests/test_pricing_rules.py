import pytest
from src.membership import Member
from src.fitness_class import FitnessClass
from src.pricing_service import calculate_price

# DECISION TABLE (KARAR TABLOSU)
# Girdiler: Üyelik Tipi, Doluluk Oranı
# Çıktı: Beklenen Fiyat
# Base Price (Taban Fiyat) hepsi için 100.0 kabul edilecek.

@pytest.mark.parametrize("membership_type, occupancy_rate, expected_price", [
    ("standard", 0.10, 100.0), # Senaryo 1: Standart üye, sınıf boş (%10) -> Fiyat aynı
    ("student",  0.10, 80.0),  # Senaryo 2: Öğrenci, sınıf boş (%10) -> %20 İndirim
    ("standard", 0.90, 120.0), # Senaryo 3: Standart, sınıf dolu (%90) -> %20 Zam (Surge)
    ("student",  0.90, 96.0),  # Senaryo 4: Öğrenci (%20 indirim) + Dolu (%20 zam) -> 80 * 1.2 = 96
])
def test_dynamic_pricing_decision_table(membership_type, occupancy_rate, expected_price):
    # Arrange (Hazırlık)
    # Kapasitesi 10 olan bir sınıf
    f_class = FitnessClass("Zumba", "Test Hoca", 10, "2025-01-01", base_price=100.0)
    
    # Doluluk oranına göre rezervasyon listesini sahte dolduruyoruz
    # Örn: 0.90 ise 9 kişi, 0.10 ise 1 kişi
    current_count = int(10 * occupancy_rate)
    f_class.reservations = [i for i in range(current_count)] # Dummy ID listesi
    
    member = Member(1, "Test Uye", membership_type)

    # Act (Eylem)
    actual_price = calculate_price(f_class, member)

    # Assert (Doğrulama)
    # Kuruş farkları olabileceği için yaklaşık eşitlik kontrolü yapıyoruz
    assert actual_price == pytest.approx(expected_price, 0.01)