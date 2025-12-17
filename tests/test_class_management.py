import pytest
from datetime import datetime
from src.fitness_class import FitnessClass

def test_create_fitness_class_successfully():
    # Arrange
    title = "Morning Yoga"
    instructor = "Gamze Hoca"
    capacity = 15
    # 2025 yılına uygun bir tarih verelim
    date_time = datetime(2025, 6, 15, 9, 0)
    base_price = 50.0

    # Act
    # Henüz FitnessClass diye bir şey yok, hata alacağız
    f_class = FitnessClass(title, instructor, capacity, date_time, base_price)

    # Assert
    assert f_class.title == "Morning Yoga"
    assert f_class.capacity == 15
    assert f_class.current_occupancy() == 0  # Başlangıçta sınıf boş olmalı
    assert isinstance(f_class.reservations, list) # Rezervasyonları tutacak bir liste olmalı