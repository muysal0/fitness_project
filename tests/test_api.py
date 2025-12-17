import pytest
import json
# Uygulamanın ana dosyası 'src/app.py' olacak diye varsayıyoruz
from src.app import app

@pytest.fixture
def client():
    # Testler için sanal bir istemci (browser gibi) oluşturur
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_api_create_member(client):
    # Arrange: Gönderilecek veri (Web sitesinden gelmiş gibi)
    payload = {
        "id": 50,
        "name": "Test Kullanicisi",
        "membership_type": "premium"
    }

    # Act: POST isteği atıyoruz
    response = client.post('/api/members', 
                           data=json.dumps(payload),
                           content_type='application/json')

    # Assert: Cevap başarılı (201 Created) olmalı
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["message"] == "Member created successfully"
    assert data["member"]["name"] == "Test Kullanicisi"

def test_api_get_member(client):
    # Arrange: Önce bir üye var varsayalım (Mocklayabiliriz veya önce create çağırabiliriz)
    # Basitlik olsun diye 404 testi yapalım (Olmayan üye)
    
    # Act: Olmayan bir üyeyi isteyelim
    response = client.get('/api/members/9999')

    # Assert: Bulunamadı (404) dönmeli
    assert response.status_code == 404

# tests/test_api.py dosyasının devamına ekle...

def test_api_list_classes(client):
    # Act: Ders listesini iste
    response = client.get('/api/classes')

    # Assert: Başarılı dönmeli ve liste olmalı
    assert response.status_code == 200
    data = json.loads(response.data)
    # Cevabın içinde "classes" anahtarı ve bir liste bekliyoruz
    assert "classes" in data
    assert isinstance(data["classes"], list)

def test_api_make_reservation(client):
    # Arrange: Rezervasyon isteği verisi
    # Not: Gerçekte var olan ID'ler olması gerekecek ama şimdilik formatı test ediyoruz
    booking_payload = {
        "member_id": 1,
        "class_id": 101
    }

    # Act: Rezervasyon yap (POST)
    response = client.post('/api/reservations',
                           data=json.dumps(booking_payload),
                           content_type='application/json')

    # Assert: 
    # Bu testin sonucu, o anki duruma göre değişebilir ama 
    # en azından sunucunun cevap verdiğini (201 veya 400 gibi) doğrulamalıyız.
    # Biz şimdilik başarılı bir senaryo bekleyelim.
    assert response.status_code in [201, 200]
    data = json.loads(response.data)
    assert "status" in data
    assert data["status"] == "confirmed"