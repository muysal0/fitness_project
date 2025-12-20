import pytest
from unittest.mock import MagicMock
from src.reservation_system import ReservationManager
# Gerçek sınıfları import etmemize bile gerek yok, çünkü onları taklit edeceğiz (Mock)

def test_book_class_success_with_mock():
    """
    Test Senaryosu: Rezervasyon başarılı olduğunda doğru işlemler yapılıyor mu?
    Yöntem: Mocking (Taklit Etme)
    """
    # 1. ARRANGE (Hazırlık)
    manager = ReservationManager()

    # SAHTE ÜYE (Member MOCK): Sadece member_id özelliği olsun yeter
    mock_member = MagicMock()
    mock_member.member_id = 101

    # SAHTE DERS (FitnessClass MOCK): 
    # İçinde gerçek mantık çalışmayacak, biz ne dersek onu döndürecek.
    mock_class = MagicMock()
    mock_class.title = "Mock Yoga"
    mock_class.capacity = 10
    
    # "current_occupancy" çağrıldığında "5" dönsün (Yani yer var)
    mock_class.current_occupancy.return_value = 5 
    
    # "reservations" listesi yerine bir Mock listesi koyuyoruz ki "append" çağrıldı mı kontrol edebilelim
    mock_class.reservations = MagicMock() 

    # 2. ACT (Eylem)
    result = manager.book_class(mock_member, mock_class)

    # 3. ASSERT (Doğrulama)
    # Sonuç başarılı dönmeli
    assert result["status"] == "confirmed"
    
    # EN ÖNEMLİ KISIM:
    # Gerçekten listeye ekleme yapmaya çalıştı mı?
    # (mock_class.reservations.append(101) çağrıldı mı?)
    mock_class.reservations.append.assert_called_once_with(101)

def test_book_class_failure_when_full_mock():
    """
    Test Senaryosu: Sınıf doluysa hata veriyor mu?
    """
    # 1. Arrange
    manager = ReservationManager()
    
    mock_member = MagicMock()
    mock_class = MagicMock()
    mock_class.capacity = 10
    
    # DOLULUK SENARYOSU:
    # current_occupancy çağrıldığında 10 dönsün (Yani Full)
    mock_class.current_occupancy.return_value = 10

    # 2. Act & Assert
    # Hata fırlatmalı
    with pytest.raises(ValueError, match="Class is full"):
        manager.book_class(mock_member, mock_class)
        
    # Sınıf dolu olduğu için "append" HİÇ ÇAĞRILMAMALI
    mock_class.reservations.append.assert_not_called()