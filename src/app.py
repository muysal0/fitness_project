import os
import time
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select

app = Flask(__name__)

@app.after_request
def add_security_headers(response):
    """
    OWASP ZAP Taraması için Güvenlik İyileştirmesi:
    Eksik olan güvenlik başlıklarını (Headers) tüm yanıtlara ekler.
    """
    # 1. Tarayıcının MIME-type tahmin etmesini engeller (Stil dosyası yerine virüs çalışmasın diye)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # 2. Sitenin başka bir site içinde (iFrame) çalışmasını engeller (Clickjacking koruması)
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # 3. XSS (Cross-Site Scripting) korumasını açar
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # 4. HTTPS zorlaması (Eğer SSL sertifikası olsaydı) - Şimdilik hazırlık olarak ekliyoruz
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response

# --- VERITABANI AYARI ---
db_url = os.environ.get('DATABASE_URL', 'sqlite:///fitness.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app, engine_options={
    "pool_pre_ping": True,  # Bağlantı koparsa otomatik tekrar dene (Retry Mechanism)
    "pool_recycle": 300,    # Bağlantıları 5 dakikada bir yenile
})

# --- MODELLER ---
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

def calculate_final_price(base_price, is_student, occupancy_rate):
    price = base_price
    
    # 1. Öğrenci İndirimi (%50)
    if is_student:
        price = price * 0.50

    # 2. Surge Pricing (Doluluk > %80 ise %20 Zam)
    if occupancy_rate > 0.80:
        price = price * 1.20

    return round(price, 2)

def calculate_refund(paid_amount, hours_until_class):
    """
    İade kuralı:
    - Derse 24 saatten fazla varsa: %100 İade
    - Derse 24 saatten az varsa: %50 İade
    - Ders saati geçtiyse (negatif saat): %0 İade (İade yok)
    """
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
                # Yeni sayım yöntemi (Warning vermez)
                count = db.session.scalar(select(FitnessClass))
                if not count:
                    c1 = FitnessClass(title="Yoga", capacity=10, base_price=100.0)
                    db.session.add(c1)
                    db.session.commit()
            print(f"Veritabani baglantisi basarili! Kullandığım DB: {app.config['SQLALCHEMY_DATABASE_URI']}")
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
    # Yeni sorgu yöntemi (select)
    classes = db.session.scalars(select(FitnessClass)).all()
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

    # DÜZELTİLEN KISIM: .query.get() yerine db.session.get()
    member = db.session.get(Member, m_id)
    if not member:
        member = Member(id=m_id)
        db.session.add(member)
    
    # DÜZELTİLEN KISIM: .query.get() yerine db.session.get()
    f_class = db.session.get(FitnessClass, c_id)
    
    if not f_class:
        return jsonify({"error": "Ders bulunamadi"}), 404

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

from sqlalchemy.exc import OperationalError

@app.errorhandler(OperationalError)
def handle_db_error(e):
    """
    Veritabanı çöktüğünde devreye girer.
    Kullanıcıya 500 HTML sayfası yerine düzgün bir JSON döner.
    """
    return jsonify({
        "error": "Service Unavailable", 
        "message": "Veritabanı bağlantısında geçici bir sorun var. Lütfen biraz sonra tekrar deneyin."
    }), 503

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)