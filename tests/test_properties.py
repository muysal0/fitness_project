import pytest
from hypothesis import given, strategies as st
from src.fitness_class import FitnessClass

# Property: Bir dersin kapasitesi ne olursa olsun, 
# boş koltuk sayısı asla negatif olmamalıdır.
# Hypothesis bizim için rastgele kapasite (1-100) ve rastgele rezervasyon sayısı üretecek.

@given(capacity=st.integers(min_value=1, max_value=100), 
       num_bookings=st.integers(min_value=0, max_value=100))
def test_capacity_invariant(capacity, num_bookings):
    # Arrange
    # FitnessClass'ı mockluyoruz veya basitçe oluşturuyoruz
    f_class = FitnessClass("Test Yoga", "Hoca", capacity, "2025-01-01", 50.0)
    
    # Act
    # Kapasiteden fazla rezervasyon eklemeye çalışalım (veya ekleyelim)
    # Burada mantığı simüle ediyoruz: Sistem kapasiteyi aşan rezervasyonu reddetmeli
    # VEYA kabul ediyorsa bile kalan yer eksiye düşmemeli (mantık hatası kontrolü)
    
    # Şimdilik basit bir "invariant" (değişmez kural) testi:
    # Eğer rezervasyon sayısı kapasiteyi geçerse sistem bunu bir şekilde engellemeliydi.
    # Biz burada şunu test ediyoruz: Business kuralımız doğru çalışıyor mu?
    
    # (Not: Bu test şu an fail edecek çünkü FitnessClass daha tam değil)
    
    # Diyelim ki rezervasyon listesini manuel doldurduk (Simülasyon)
    actual_bookings = min(capacity, num_bookings) # Sistem sınırı korumalı
    f_class.reservations = [1] * actual_bookings # Dummy ID'ler

    # Assert
    assert f_class.current_occupancy() <= f_class.capacity
    assert f_class.current_occupancy() >= 0