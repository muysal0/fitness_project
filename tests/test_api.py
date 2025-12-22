import pytest
import json
import os
from src.app import app, db, Member, FitnessClass

@pytest.fixture
def client():
    # Test Modu
    app.config['TESTING'] = True
    
    # KRİTİK DEĞİŞİKLİK:
    # Eğer dışarıdan (CI/CD'den) bir DATABASE_URL geliyorsa onu kullan.
    # Gelmiyorsa (lokal test) RAM'deki SQLite'ı kullan.
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url

    with app.test_client() as client:
        with app.app_context():
            # Tabloları oluştur
            db.create_all()
            
            # Test verisi ekle
            # (Postgres'te id conflict olmasın diye check yapıyoruz)
            if not db.session.get(FitnessClass, 1):
                c1 = FitnessClass(id=1, title="Test Yoga", capacity=10, base_price=100.0)
                db.session.add(c1)
                db.session.commit()
        
        yield client
        
        # Test bitince temizlik yap (Postgres ise tabloları boşalt)
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_api_list_classes(client):
    """Ders listesi kontrolü"""
    response = client.get('/api/classes')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "classes" in data
    # Test verisi eklendiği için en az 1 ders olmalı
    assert len(data["classes"]) >= 1

def test_api_make_reservation_success(client):
    """Başarılı rezervasyon"""
    payload = {"member_id": 101, "class_id": 1}
    response = client.post('/api/reservations', json=payload)
    assert response.status_code == 201

def test_api_make_reservation_duplicate(client):
    """Çifte kayıt engelleme"""
    payload = {"member_id": 102, "class_id": 1}
    
    # 1. Kayıt
    client.post('/api/reservations', json=payload)
    
    # 2. Kayıt (Hata vermeli)
    response = client.post('/api/reservations', json=payload)
    assert response.status_code == 400
    assert "Zaten" in json.loads(response.data)["error"]

def test_api_invalid_class(client):
    """Olmayan ID testi"""
    payload = {"member_id": 103, "class_id": 9999}
    response = client.post('/api/reservations', json=payload)
    assert response.status_code == 404