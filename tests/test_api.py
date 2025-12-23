import pytest
import json
import os
from unittest.mock import patch
from src.app import app, db, Member, FitnessClass, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # RAM veritabanı kullan
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url

    with app.test_client() as client:
        with app.app_context():
            # KRİTİK DÜZELTME: Önce her şeyi sil, sonra temiz kur.
            db.drop_all() 
            db.create_all()
            
            # Şimdi kendi test verimizi zorla ekliyoruz (Kapasite: 2)
            c1 = FitnessClass(id=1, title="Test Yoga", capacity=2, base_price=100.0)
            db.session.add(c1)
            db.session.commit()
        
        yield client
        
        # Test bitince temizlik
        with app.app_context():
            db.session.remove()
            db.drop_all()

# --- STANDART TESTLER ---
def test_api_list_classes(client):
    """Mutant 13'ü yakalar (Kapasite 0 gelirse patlar)"""
    response = client.get('/api/classes')
    data = json.loads(response.data)
    assert len(data["classes"]) >= 1
    # Artık veritabanını sıfırladığımız için burası kesinlikle 2 gelecek
    assert data["classes"][0]["capacity"] == 2 

def test_api_make_reservation_success(client):
    """Mutant 12'yi yakalar (200 gelirse patlar)"""
    response = client.post('/api/reservations', json={"member_id": 101, "class_id": 1})
    assert response.status_code == 201

def test_api_make_reservation_duplicate(client):
    """Mutant 10'u yakalar"""
    client.post('/api/reservations', json={"member_id": 102, "class_id": 1})
    response = client.post('/api/reservations', json={"member_id": 102, "class_id": 1})
    assert response.status_code == 400

def test_api_invalid_class(client):
    """Mutant 11'i yakalar"""
    response = client.post('/api/reservations', json={"member_id": 103, "class_id": 9999})
    assert response.status_code == 404

def test_capacity_limit(client):
    """Mutant 8 ve 9'u yakalar"""
    # Kapasite 2. Sınıfı dolduruyoruz.
    # 1. Kişi
    client.post('/api/reservations', json={"member_id": 201, "class_id": 1})
    # 2. Kişi (Dolu)
    client.post('/api/reservations', json={"member_id": 202, "class_id": 1})
    
    # 3. Kişi (HATA ALMALI)
    response = client.post('/api/reservations', json={"member_id": 203, "class_id": 1})
    assert response.status_code == 400
    assert "dolu" in json.loads(response.data)["error"].lower()

# --- FİYATLANDIRMA TESTLERİ (Hassas Kontrol) ---

def test_check_student_discount(client):
    """Mutant 1, 2, 14'ü yakalar"""
    # %50 İndirim -> 100 * 0.5 = 50.0
    response = client.get('/api/classes?student=true')
    data = json.loads(response.data)
    assert data["classes"][0]["final_price"] == 50.0

def test_check_surge_pricing(client):
    """Mutant 3, 4, 5, 6'yı yakalar"""
    # Sınıfı doldur (%100 > %80) -> Zam gelmeli
    with app.app_context():
        c1 = db.session.get(FitnessClass, 1)
        # Önceki testlerden kalanları temizleyelim, garanti olsun
        c1.attendees = []
        m1 = Member(id=901); m2 = Member(id=902)
        c1.attendees.append(m1); c1.attendees.append(m2)
        db.session.commit()

    # Zamlı Fiyat: 100 * 1.2 = 120.0
    response = client.get('/api/classes?student=false')
    data = json.loads(response.data)
    assert data["classes"][0]["final_price"] == 120.0

def test_price_rounding(client):
    """Mutant 7'yi yakalar"""
    with app.app_context():
        c1 = db.session.get(FitnessClass, 1)
        c1.base_price = 100.11 # Küsüratlı fiyat
        # Listeyi boşalt (Zam olmasın)
        c1.attendees = []
        db.session.commit()
    
    response = client.get('/api/classes?student=false')
    final = json.loads(response.data)["classes"][0]["final_price"]
    
    # Zam yokken: 100.11
    assert final == 100.11

def test_db_retry_logic():
    """Mutant 15'i yakalar"""
    with patch('src.app.db.create_all') as mock_create:
        mock_create.side_effect = [Exception("Fail"), None]
        init_db()
        assert mock_create.call_count >= 2