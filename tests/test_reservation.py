import pytest
from src.membership import Member
from src.fitness_class import FitnessClass
# Rezervasyon işlemlerini yönetecek bir manager sınıfı hayal ediyoruz
from src.reservation_system import ReservationManager

def test_make_reservation_success():
    # Arrange (Hazırlık)
    # Kapasitesi 10 olan boş bir sınıf
    pilates = FitnessClass("Pilates", "Ceren Hoca", 10, "2025-06-21", 100.0)
    member = Member(101, "Mehmet", "standard")
    manager = ReservationManager()

    # Act (Eylem)
    # Mehmet rezervasyon yapıyor
    confirmation = manager.book_class(member, pilates)

    # Assert (Doğrulama)
    assert confirmation["status"] == "confirmed"
    assert member.member_id in pilates.reservations  # Mehmet'in ID'si listeye girmeli
    assert len(pilates.reservations) == 1            # Doluluk 1 olmalı

def test_prevent_booking_when_full():
    # Arrange
    # Kapasitesi sadece 2 kişi olan özel ders
    private_lesson = FitnessClass("Boxing", "Rocky", 2, "2025-06-21", 200.0)
    member_late = Member(999, "Gec Kalan", "standard")
    manager = ReservationManager()

    # Sınıfı manuel olarak dolduralım (Zaten 2 kişi var)
    private_lesson.reservations = [101, 102]

    # Act & Assert (Eylem ve Doğrulama)
    # Dolu sınıfa kayıt yapmaya çalışınca ValueError hatası bekliyoruz
    with pytest.raises(ValueError, match="Class is full"):
        manager.book_class(member_late, private_lesson)

def test_prevent_duplicate_booking():
    # Arrange
    zumba = FitnessClass("Zumba", "Asli Hoca", 10, "2025-06-22", 80.0)
    member = Member(55, "Tekrar Eden Uye", "standard")
    manager = ReservationManager()

    # İlk rezervasyon başarılı olmalı
    manager.book_class(member, zumba)

    # Act & Assert
    with pytest.raises(ValueError, match="Member already booked"):
        manager.book_class(member, zumba)