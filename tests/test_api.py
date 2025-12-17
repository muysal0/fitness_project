import pytest
import json
from src.app import app, init_db, classes_db, members_db

@pytest.fixture
def client():
    # Test ortamını hazırla
    app.config['TESTING'] = True
    
    # Her testten önce veritabanını sıfırla ve yeniden başlat
    classes_db.clear()
    members_db.clear()
    init_db() 
    
    with app.test_client() as client:
        yield client

def test_api_list_classes(client):
    # Act: Ders listesini iste
    response = client.get('/api/classes')

    # Assert: Başarılı dönmeli
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "classes" in data
    assert len(data["classes"]) > 0
    # Yeni eklediğimiz "time" alanı gelmiş mi?
    assert "time" in data["classes"][0]

def test_api_make_reservation(client):
    # Arrange
    payload = {
        "member_id": 101,
        "class_id": 101, # Morning Yoga 08:00
        "membership_type": "standard"
    }

    # Act
    response = client.post('/api/reservations', 
                           json=payload,
                           content_type='application/json')

    # Assert
    assert response.status_code == 201 or response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "confirmed"

def test_api_cancel_reservation(client):
    # Arrange: Önce rezervasyon yap
    setup_payload = {
        "member_id": 99, 
        "class_id": 101,
        "membership_type": "standard"
    }
    client.post('/api/reservations', json=setup_payload)

    # Act: İptal isteği (DELETE) at
    delete_payload = {
        "member_id": 99, 
        "class_id": 101
    }
    response = client.delete('/api/reservations', 
                             json=delete_payload,
                             content_type='application/json')

    # Assert
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "cancelled successfully" in data["message"]

def test_api_check_student_price(client):
    # Arrange: Öğrenci filtresi ile dersleri iste
    response = client.get('/api/classes?student=true')
    
    # Assert
    assert response.status_code == 200
    data = json.loads(response.data)
    first_class = data["classes"][0]
    
    # Base price 100 ise final price 50 olmalı (%50 indirim)
    # Not: Hangi dersin geldiğine göre base_price değişebilir, orana bakıyoruz.
    base = first_class["base_price"]
    final = first_class["final_price"]
    
    # İndirim uygulanmış mı? (Final fiyat taban fiyattan düşük olmalı)
    assert final < base
    assert final == base * 0.5