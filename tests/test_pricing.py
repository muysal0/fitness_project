import pytest
from src.membership import Member
from src.fitness_class import FitnessClass
# Fiyat hesaplamasını ayrı bir serviste yapmak temiz kod (Clean Code) için iyidir
from src.pricing_service import calculate_price

def test_student_gets_discount():
    # Arrange (Hazırlık)
    # Taban fiyatı 100 TL olan bir ders
    yoga_class = FitnessClass("Yoga", "Guru", 20, "2025-06-20", base_price=100.0)
    
    student = Member(1, "Ogrenci Can", "student")
    standard = Member(2, "Normal Can", "standard")

    # Act (Eylem)
    # Henüz calculate_price fonksiyonumuz yok, hata verecek
    price_for_student = calculate_price(yoga_class, student)
    price_for_standard = calculate_price(yoga_class, standard)

    # Assert (Doğrulama)
    # Öğrenci fiyatı, standart fiyattan düşük olmalı
    assert price_for_student < price_for_standard
    # Beklentimiz %20 indirim ise 80 TL olmalı
    assert price_for_student == 80.0

def test_surge_pricing_high_demand():
    # Arrange
    # Kapasitesi 10 olan bir ders
    spin_class = FitnessClass("Spinning", "Ece", 10, "2025-06-20", base_price=100.0)
    standard_member = Member(3, "Ayse", "standard")

    # Sınıfı yapay olarak dolduralım (Listeye 9 tane dummy ID atıyoruz, %90 doluluk)
    # Not: Henüz FitnessClass içinde reservations listesi tam tanımlı değil ama varmış gibi test yazıyoruz
    spin_class.reservations = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    # Act
    final_price = calculate_price(spin_class, standard_member)

    # Assert
    # Doluluk %80'i geçtiği için fiyat taban fiyattan yüksek olmalı
    assert final_price > 100.0