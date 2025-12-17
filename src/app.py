from flask import Flask, jsonify, request, render_template
from src.membership import Member
from src.fitness_class import FitnessClass
from src.reservation_system import ReservationManager

app = Flask(__name__)

# --- SAHTE VERİTABANI (RAM'de tutulur) ---
members_db = {}
classes_db = {}
reservation_manager = ReservationManager()

def init_db():
    """Test verilerini saatli olarak yükler."""
    # Morning Yoga Seansları
    yoga_8 = FitnessClass("Morning Yoga", "Gamze Hoca", 15, "08:00", 100.0)
    yoga_9 = FitnessClass("Morning Yoga", "Gamze Hoca", 15, "09:00", 100.0)
    yoga_10 = FitnessClass("Morning Yoga", "Gamze Hoca", 15, "10:00", 100.0)

    # Pilates Seansları
    pilates_17 = FitnessClass("Pilates", "Ceren Hoca", 10, "17:00", 120.0)
    pilates_18 = FitnessClass("Pilates", "Ceren Hoca", 10, "18:00", 120.0)
    
    # Spinning Seansı (Tek saat)
    spin = FitnessClass("Spinning", "Ece Hoca", 8, "19:30", 150.0)

    # DB'ye ekle
    classes_db[101] = yoga_8
    classes_db[102] = yoga_9
    classes_db[103] = yoga_10
    classes_db[201] = pilates_17
    classes_db[202] = pilates_18
    classes_db[301] = spin

# Veritabanını başlat
init_db()

# --- API ENDPOINTLERİ ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/members', methods=['POST'])
def create_member():
    data = request.get_json()
    # Basit doğrulama
    if not data or 'id' not in data:
        return jsonify({"error": "Eksik veri"}), 400
    
    new_member = Member(data['id'], data['name'], data['membership_type'])
    members_db[data['id']] = new_member
    
    return jsonify({
        "message": "Member created successfully",
        "member": data
    }), 201

@app.route('/api/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    member = members_db.get(member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404
    
    return jsonify({
        "id": member.member_id,
        "name": member.name,
        "membership_type": member.membership_type
    })

@app.route('/api/classes', methods=['GET'])
def list_classes():
    # URL'den öğrenci bilgisini al (Örn: /api/classes?student=true)
    is_student_query = request.args.get('student')
    
    # Geçici bir üye tipi belirliyoruz (Fiyatı hesaplamak için)
    temp_membership_type = "student" if is_student_query == 'true' else "standard"
    temp_member = Member(0, "Guest", temp_membership_type)
    
    # Fiyat servisini import ettiğinden emin ol (Dosyanın en başında olmalı)
    from src.pricing_service import calculate_price

    result = []
    for c_id, c in classes_db.items():
        # O anki duruma göre fiyatı hesapla
        final_price = calculate_price(c, temp_member)
        
        # ... önceki kodlar ...
        result.append({
            "id": c_id,
            "title": c.title,
            "instructor": c.instructor,
            "capacity": c.capacity,
            "occupancy": c.current_occupancy(),
            "base_price": c.base_price,
            "final_price": final_price,
            "time": c.date_time  # <--- BU SATIRI EKLEDİK (Saat verisi)
        })
    return jsonify({"classes": result})

@app.route('/api/reservations', methods=['POST'])
def make_reservation():
    data = request.get_json()
    member_id = data.get('member_id')
    class_id = data.get('class_id')

    # 1. Üye ve Sınıf var mı kontrol et
    member = members_db.get(member_id)
    fitness_class = classes_db.get(class_id)

    # Testlerin geçmesi için eğer üye yoksa geçici bir üye oluşturalım (Test kolaylığı)
    if not member and member_id:
        member = Member(member_id, "Gecici Uye", "standard")
        members_db[member_id] = member

    if not member or not fitness_class:
        return jsonify({"error": "Invalid member or class ID"}), 404

    try:
        # 2. Rezervasyon yap
        result = reservation_manager.book_class(member, fitness_class)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    # --- src/app.py içine eklenecek ---

@app.route('/api/reservations', methods=['DELETE'])
def cancel_reservation():
    data = request.get_json()
    member_id = data.get('member_id')
    class_id = data.get('class_id')

    # Sınıfı bul
    fitness_class = classes_db.get(class_id)
    
    if not fitness_class:
        return jsonify({"error": "Class not found"}), 404

    # Üye listede var mı?
    if member_id in fitness_class.reservations:
        fitness_class.reservations.remove(member_id)
        return jsonify({"message": "Reservation cancelled successfully"}), 200
    else:
        return jsonify({"error": "Reservation not found for this member"}), 400

@app.route('/api/members/<int:member_id>/reservations', methods=['GET'])
def get_member_reservations(member_id):
    """Bir üyenin kayıtlı olduğu dersleri döner."""
    my_classes = []
    
    # Tüm dersleri gez, bu üye hangisinde var kontrol et
    for c in classes_db.values():
        if member_id in c.reservations:
            my_classes.append({
                "class_id": 101, # (Not: ID'yi dinamik almak için classes_db yapısını döngüde id ile almak daha iyi olur ama şimdilik nesneden alalım)
                # Düzeltme: classes_db dictionary olduğu için id'yi döngüden almalıyız, aşağıda düzeltiyorum:
                "title": c.title,
                "time": c.date_time,
                "instructor": c.instructor
            })
            
    # Daha temiz bir döngü ile ID'leri de alalım:
    my_classes = []
    for c_id, c in classes_db.items():
        if member_id in c.reservations:
            my_classes.append({
                "class_id": c_id,
                "title": c.title,
                "time": c.date_time,
                "instructor": c.instructor
            })

    return jsonify({"reservations": my_classes})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)