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