import pytest
import json
import os
from src.app import app, db, Member, FitnessClass

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Test verileri ekle
            c1 = FitnessClass(title="Yoga", capacity=10, base_price=100.0)
            db.session.add(c1)
            
            m1 = Member(id=101, membership_type="standard")
            db.session.add(m1)
            
            # Üyeyi derse kaydet (İptal ve Admin testi için)
            m1.classes.append(c1)
            
            db.session.commit()
        
        yield client
        
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_login_flow(client):
    """Login API'sini test et"""
    # 1. Yeni Üye Girişi
    res = client.post('/api/login', json={"id": 999, "type": "student"})
    assert res.status_code == 200
    assert res.json["status"] == "new"

    # 2. Var Olan Üye (Aynı Tip)
    res = client.post('/api/login', json={"id": 999, "type": "student"})
    assert res.json["status"] == "ok"

    # 3. Var Olan Üye (Farklı Tip - Uyarı Vermeli)
    res = client.post('/api/login', json={"id": 999, "type": "standard"})
    assert res.json["status"] == "warning"

def test_admin_panel(client):
    """Admin API'sini test et"""
    res = client.get('/api/admin/all')
    assert res.status_code == 200
    data = res.json
    # En az 1 kayıt olmalı (Fixture ekledi)
    assert len(data) >= 1
    assert data[0]["class_title"] == "Yoga"

def test_my_reservations(client):
    """Rezervasyonlarım API'sini test et"""
    # Kaydı olan üye
    res = client.get('/api/members/101/reservations')
    assert len(res.json["reservations"]) == 1
    
    # Kaydı olmayan üye
    res = client.get('/api/members/999/reservations')
    assert len(res.json["reservations"]) == 0

def test_cancel_reservation(client):
    """İptal işlemini test et"""
    # Başarılı İptal
    payload = {"member_id": 101, "class_id": 1}
    res = client.delete('/api/reservations', json=payload)
    assert res.status_code == 200
    
    # Olmayan İptal (Hata vermeli)
    res = client.delete('/api/reservations', json=payload)
    assert res.status_code == 404

def test_reset_db(client):
    """Reset API'sini test et"""
    res = client.post('/api/reset')
    assert res.status_code == 200