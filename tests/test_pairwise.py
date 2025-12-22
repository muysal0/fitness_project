import pytest
from src.app import calculate_final_price

# PAIRWISE (İKİLİ) TEST SENARYOLARI
# Amaç: Tüm parametre çiftlerini en az bir kez test etmek.
# Bu tablo PICT/ACTS mantığıyla oluşturulmuştur.

# Parametreler:
# 1. Membership: Standard, Student, Premium
# 2. Class Type: Yoga (100 TL), Spinning (150 TL)
# 3. Occupancy: Low (0.5), High (0.9 - Surge Pricing)
# 4. Time: Morning, Evening (Şimdilik fiyata etkisi yok ama kombinasyonda var)

@pytest.mark.parametrize("membership, class_type, occupancy, time, expected_price", [
    # Senaryo 1: Standart, Yoga, Düşük, Sabah -> 100 TL
    ("standard", "yoga", 0.5, "morning", 100.0),

    # Senaryo 2: Standart, Spinning, Yüksek, Akşam -> 150 * 1.2 = 180 TL
    ("standard", "spinning", 0.9, "evening", 180.0),

    # Senaryo 3: Öğrenci, Yoga, Yüksek, Akşam -> (100 * 1.2) * 0.5 = 60 TL
    ("student", "yoga", 0.9, "evening", 60.0),

    # Senaryo 4: Öğrenci, Spinning, Düşük, Sabah -> 150 * 0.5 = 75 TL
    ("student", "spinning", 0.5, "morning", 75.0),

    # Senaryo 5: Premium, Yoga, Yüksek, Sabah -> (Premium'a indirim yoksa standart gibi) -> 100 * 1.2 = 120 TL
    # (Not: Kodumuzda Premium için özel kural yok, standart davranır)
    ("premium", "yoga", 0.9, "morning", 120.0),

    # Senaryo 6: Premium, Spinning, Düşük, Akşam -> 150 TL
    ("premium", "spinning", 0.5, "evening", 150.0),
])
def test_pairwise_combinations(membership, class_type, occupancy, time, expected_price):
    # Arrange
    base_price = 100.0 if class_type == "yoga" else 150.0
    is_student = (membership == "student")
    
    # Act
    # Not: calculate_final_price fonksiyonumuz şu an 'time' parametresini kullanmıyor 
    # ama kombinatoryal testte bu parametrenin varlığı önemlidir.
    actual_price = calculate_final_price(base_price, is_student, occupancy)

    # Assert
    assert actual_price == expected_price