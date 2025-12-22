import os
import time
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select

app = Flask(__name__)

db_url = os.environ.get('DATABASE_URL', 'sqlite:///fitness.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

# --- İŞ MANTIĞI FONKSİYONLARI (TESTLER İÇİN GEREKLİ) ---
def calculate_final_price(base_price, is_student, occupancy_rate):
    price = base_price
    
    # Kural 1: Öğrenci İndirimi
    if is_student:
        price = price * 0.50
        
    # Kural 2: Surge Pricing
    if occupancy_rate > 0.80:
        price = price * 1.20
        
    return round(price, 2)

def calculate_refund(paid_amount, hours_until_class):
    if hours_until_class < 0:
        return 0.0
    elif hours_until_class < 24:
        return paid_amount * 0.50
    else:
        return paid_amount

# --- DB BAŞLATMA ---
def init_db():
    retries = 5
    while retries > 0:
        try:
            with app.app_context():
                db.create_all()
                if not db.session.scalar(select(FitnessClass)):
                    c1 = FitnessClass(title="Yoga", capacity=10, base_price=100.0)
                    db.session.add(c1)
                    db.session.commit()
            print("Veritabani baglantisi basarili!")
            break
        except Exception as e:
            print(f"DB Baglanamadi... {e}")
            time.sleep(2)
            retries -= 1

@app.route('/')
def home():
    return "Sistem Calisiyor!"

@app.route('/api/classes', methods=['GET'])
def list_classes():
    is_student = request.args.get('student') == 'true'
    classes = db.session.scalars(select(FitnessClass)).all()
    result = []
    
    for c in classes:
        # Doluluk Oranı
        occupancy = c.attendees.count()
        occupancy_rate = occupancy / c.capacity if c.capacity > 0 else 0
        
        # Fiyatı fonksiyonla hesapla (Böylece hem test hem api aynı kodu kullanır)
        final_price = calculate_final_price(c.base_price, is_student, occupancy_rate)

        result.append({
            "id": c.id,
            "title": c.title,
            "capacity": c.capacity,
            "occupancy": occupancy,
            "base_price": c.base_price,
            "final_price": final_price
        })
    return jsonify({"classes": result})

@app.route('/api/reservations', methods=['POST'])
def make_reservation():
    data = request.get_json()
    m_id = data.get('member_id')
    c_id = data.get('class_id')

    member = db.session.get(Member, m_id)
    if not member:
        member = Member(id=m_id)
        db.session.add(member)
    
    f_class = db.session.get(FitnessClass, c_id)
    
    if not f_class:
        return jsonify({"error": "Ders bulunamadi"}), 404

    if f_class in member.classes:
        return jsonify({"error": "Zaten kayitlisin"}), 400

    if f_class.attendees.count() >= f_class.capacity:
        return jsonify({"error": "Kontenjan dolu"}), 400

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
    init_db()
    app.run(host='0.0.0.0', port=5000)