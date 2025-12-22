import pytest
import json
from src.app import app, db, Member, FitnessClass

@pytest.fixture
def client():
    # Testler için geçici bir yapılandırma
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # RAM'de çalışan hızlı DB
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Test verilerini ekle
            c1 = FitnessClass(title="Test Yoga", capacity=10, base_price=100.0)
            db.session.add(c1)
            db.session.commit()
        
        yield client
        
        # Test bitince temizle
        with app.app_context():
            db.drop_all()

def test_api_list_classes(client):
    """Ders listesi geliyor mu?"""
    response = client.get('/api/classes')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "classes" in data
    assert len(data["classes"]) == 1
    assert data["classes"][0]["title"] == "Test Yoga"

def test_api_make_reservation_success(client):
    """Başarılı rezervasyon testi"""
    payload = {
        "member_id": 101,
        "class_id": 1
    }
    response = client.post('/api/reservations', 
                           json=payload,
                           content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["message"] == "Kayit Basarili"

def test_api_make_reservation_duplicate(client):
    """Çifte kayıt engelleme testi"""
    payload = {"member_id": 101, "class_id": 1}
    
    # 1. Kayıt (Başarılı)
    client.post('/api/reservations', json=payload)
    
    # 2. Kayıt (Hata vermeli)
    response = client.post('/api/reservations', json=payload)
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "Zaten kayitlisin" in data["error"]

def test_api_invalid_class(client):
    """Olmayan ders ID testi"""
    payload = {"member_id": 101, "class_id": 999}
    response = client.post('/api/reservations', json=payload)
    assert response.status_code == 404