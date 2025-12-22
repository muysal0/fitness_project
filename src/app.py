import os
import time
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- VERITABANI AYARI ---
# Docker'dan gelen URL'yi al, yoksa SQLite kullan
db_url = os.environ.get('DATABASE_URL', 'sqlite:///fitness.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELLER ---
# Ara tablo (Çoka-Çok ilişki)
reservations = db.Table('reservations',
    db.Column('member_id', db.Integer, db.ForeignKey('member.id'), primary_key=True),
    db.Column('fitness_class_id', db.Integer, db.ForeignKey('fitness_class.id'), primary_key=True)
)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), default="Standart Uye")
    membership_type = db.Column(db.String(20), default="standard")
    classes = db.relationship('FitnessClass', secondary=reservations, backref=db.backref('attendees', lazy='dynamic'))

class FitnessClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, default=10)
    base_price = db.Column(db.Float, default=100.0)

# --- DB BAŞLATMA (RETRY MANTIKLI) ---
def init_db():
    retries = 5
    while retries > 0:
        try:
            with app.app_context():
                db.create_all()
                if FitnessClass.query.count() == 0:
                    c1 = FitnessClass(title="Yoga", capacity=10, base_price=100.0)
                    db.session.add(c1)
                    db.session.commit()
            print("Veritabani baglantisi basarili!")
            break
        except Exception as e:
            print(f"DB Baglanamadi, tekrar deneniyor... Hata: {str(e)}")
            time.sleep(2)
            retries -= 1

# --- API ENDPOINTLERI ---
@app.route('/')
def home():
    return "Sistem Calisiyor!"

@app.route('/api/classes', methods=['GET'])
def list_classes():
    classes = FitnessClass.query.all()
    result = []
    for c in classes:
        result.append({
            "id": c.id,
            "title": c.title,
            "capacity": c.capacity,
            "base_price": c.base_price
        })
    return jsonify({"classes": result})

@app.route('/api/reservations', methods=['POST'])
def make_reservation():
    data = request.get_json()
    m_id = data.get('member_id')
    c_id = data.get('class_id')

    # Üye var mı? Yoksa oluştur.
    member = Member.query.get(m_id)
    if not member:
        member = Member(id=m_id)
        db.session.add(member)
    
    # Ders var mı?
    f_class = FitnessClass.query.get(c_id)
    if not f_class:
        return jsonify({"error": "Ders bulunamadi"}), 404

    # Çifte kayıt kontrolü
    if f_class in member.classes:
        return jsonify({"error": "Zaten kayitlisin"}), 400

    member.classes.append(f_class)
    db.session.commit()
    return jsonify({"message": "Kayit Basarili"}), 201

@app.route('/api/reset', methods=['POST'])
def reset():
    db.drop_all()
    db.create_all()
    init_db()
    return jsonify({"message": "Resetlendi"})

if __name__ == '__main__':
    # DB'yi sadece main'de başlat
    init_db()
    app.run(host='0.0.0.0', port=5000)