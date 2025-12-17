import pytest
from src.membership import Member
from src.fitness_class import FitnessClass
from src.pricing_service import calculate_price

def test_student_gets_discount():
    # Arrange
    yoga_class = FitnessClass("Yoga", "Guru", 20, "2025-06-20", base_price=100.0)
    
    student = Member(1, "Ogrenci Can", "student")
    standard = Member(2, "Normal Can", "standard")

    # Act
    price_for_student = calculate_price(yoga_class, student)
    price_for_standard = calculate_price(yoga_class, standard)

    # Assert
    # KURAL DEĞİŞTİ: Artık %50 indirim var. 100 TL -> 50 TL olmalı.
    assert price_for_student == 50.0 
    assert price_for_standard == 100.0

def test_surge_pricing_high_demand():
    # Arrange
    spin_class = FitnessClass("Spinning", "Ece", 10, "2025-06-20", base_price=100.0)
    standard_member = Member(3, "Ayse", "standard")

    # Sınıfı doldur (%90 doluluk)
    spin_class.reservations = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    # Act
    final_price = calculate_price(spin_class, standard_member)

    # Assert
    # %20 zam gelmeli: 100 * 1.2 = 120 TL
    assert final_price == 120.0