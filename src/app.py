import os
import time
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

app = Flask(__name__)

db_url = os.environ.get('DATABASE_URL', 'sqlite:///fitness.db')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app, engine_options={"pool_pre_ping": True, "pool_recycle": 300})

@app.errorhandler(OperationalError)
def handle_db_error(e):
    return jsonify({
        "error": "Service Unavailable",
        "message": "Veritabanı bağlantısında geçici bir sorun var. Lütfen biraz sonra tekrar deneyin."
    }), 503

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
    instructor = db.Column(db.String(50), default="Eğitmen")
    time = db.Column(db.String(20), default="09:00")
    capacity = db.Column(db.Integer, default=10)
    base_price = db.Column(db.Float, default=100.0)

# --- İŞ MANTIĞI ---
def calculate_final_price(base_price, is_student, occupancy_rate, time_str):
    price = base_price
    # Kodu tek satıra indirdik ki mutasyon scripti karıştırmasın
    try:
        if 17 <= int(time_str.split(':')[0]) <= 21: price *= 1.20
    except: pass

    if is_student: price *= 0.50
    
    # BURASI ÖNEMLİ: Tek satır yaptık
    if occupancy_rate > 0.80: price *= 1.20
    
    return round(price, 2)

def calculate_refund(paid_amount, hours):
    if hours < 0: return 0.0
    elif hours < 24: return paid_amount * 0.50
    else: return paid_amount

def init_db():
    retries = 5
    while retries > 0:
        try:
            with app.app_context():
                db.create_all()
                if not db.session.scalar(select(FitnessClass)):
                    classes = [
                        FitnessClass(title="Yoga", instructor="Gamze Hoca", time="09:00", capacity=12, base_price=100.0),
                        FitnessClass(title="Yoga", instructor="Gamze Hoca", time="19:00", capacity=12, base_price=100.0),
                        FitnessClass(title="Pilates", instructor="Ceren Hoca", time="10:00", capacity=10, base_price=120.0),
                        FitnessClass(title="Pilates", instructor="Ceren Hoca", time="18:00", capacity=10, base_price=120.0),
                        FitnessClass(title="Spinning", instructor="Mehmet Hoca", time="08:00", capacity=20, base_price=90.0),
                        FitnessClass(title="Spinning", instructor="Mehmet Hoca", time="20:00", capacity=20, base_price=90.0),
                        FitnessClass(title="Zumba", instructor="Ayşe Hoca", time="14:00", capacity=25, base_price=80.0),
                        FitnessClass(title="Zumba", instructor="Ayşe Hoca", time="17:00", capacity=25, base_price=80.0),
                        FitnessClass(title="Kick Boks", instructor="Ahmet Hoca", time="12:00", capacity=15, base_price=140.0),
                        FitnessClass(title="Kick Boks", instructor="Ahmet Hoca", time="21:00", capacity=15, base_price=140.0),
                        FitnessClass(title="CrossFit", instructor="Burak Hoca", time="15:00", capacity=10, base_price=150.0),
                        FitnessClass(title="CrossFit", instructor="Burak Hoca", time="19:00", capacity=10, base_price=150.0)
                    ]
                    db.session.add_all(classes)
                    db.session.commit()
            print("✅ Veritabani hazir!")
            break
        except Exception as e:
            print(f"⏳ Bekleniyor... {e}"); time.sleep(2); retries -= 1

@app.route('/')
def home(): return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login_check():
    data = request.get_json()
    m_id, req_type = data.get('id'), data.get('type')
    member = db.session.get(Member, m_id)
    if not member:
        member = Member(id=m_id, membership_type=req_type)
        db.session.add(member); db.session.commit()
        return jsonify({"status": "new", "actual_type": req_type})
    if member.membership_type != req_type:
        msg = f"Daha önce {member.membership_type} girişi yaptınız."
        return jsonify({"status": "warning", "actual_type": member.membership_type, "message": msg})
    return jsonify({"status": "ok", "actual_type": member.membership_type})

@app.route('/api/classes', methods=['GET'])
def list_classes():
    # MUTANT 14 İÇİN DEĞİŞKEN ADI DÜZELTİLDİ: req_student
    req_student = request.args.get('student') == 'true'
    member_id = request.args.get('member_id')
    is_student = req_student

    if member_id:
        existing = db.session.get(Member, member_id)
        if existing: is_student = (existing.membership_type == 'student')

    classes = db.session.scalars(select(FitnessClass)).all()
    result = []
    for c in classes:
        rate = c.attendees.count() / c.capacity if c.capacity > 0 else 0
        
        # calculate_final_price fonksiyonunu kullanıyoruz
        final = calculate_final_price(c.base_price, is_student, rate, c.time)
        
        result.append({
            "id": c.id, "title": c.title, "instructor": c.instructor, "time": c.time,
            "capacity": c.capacity, "occupancy": c.attendees.count(), "final_price": final, "base_price": c.base_price
        })
    return jsonify({"classes": result})

@app.route('/api/reservations', methods=['POST'])
def make_reservation():
    data = request.get_json()
    m_id, c_id = data.get('member_id'), data.get('class_id')
    member = db.session.get(Member, m_id)
    if not member:
        member = Member(id=m_id, membership_type=data.get('membership_type', 'standard'))
        db.session.add(member)
    f_class = db.session.get(FitnessClass, c_id)
    
    if not f_class: return jsonify({"error": "Ders bulunamadi"}), 404
    if f_class in member.classes: return jsonify({"error": "Zaten kayitlisin"}), 400
    if f_class.attendees.count() >= f_class.capacity: return jsonify({"error": "Kontenjan dolu"}), 400
    
    member.classes.append(f_class)
    db.session.commit()
    return jsonify({"message": "Kayit Basarili"}), 201

@app.route('/api/reservations', methods=['DELETE'])
def cancel_reservation():
    data = request.get_json()
    member = db.session.get(Member, data.get('member_id'))
    f_class = db.session.get(FitnessClass, data.get('class_id'))
    if member and f_class and f_class in member.classes:
        member.classes.remove(f_class)
        db.session.commit()
        return jsonify({"message": "Iptal edildi"}), 200
    return jsonify({"error": "Bulunamadi"}), 404

@app.route('/api/members/<int:m_id>/reservations', methods=['GET'])
def my_reservations(m_id):
    member = db.session.get(Member, m_id)
    if not member: return jsonify({"reservations": []})
    res = [{"class_id": c.id, "title": c.title, "instructor": c.instructor, "time": c.time} for c in member.classes]
    return jsonify({"reservations": res})

@app.route('/api/admin/all', methods=['GET'])
def admin_all_data():
    members = db.session.scalars(select(Member)).all()
    data = []
    for m in members:
        for c in m.classes:
            data.append({ "member_id": m.id, "type": "Öğrenci" if m.membership_type == 'student' else "Standart", "class_title": c.title, "class_time": c.time, "class_id": c.id })
    return jsonify(data)

@app.route('/api/reset', methods=['POST'])
def reset():
    db.drop_all(); db.create_all(); init_db()
    return jsonify({"message": "Resetlendi"})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)