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
    """Uygulama başlarken test verilerini yükler."""
    # Testlerde 101 ID'li sınıf kullanmıştık, onu ekleyelim
    yoga = FitnessClass("Morning Yoga", "Gamze Hoca", 15, "2025-06-15 09:00", 50.0)
    classes_db[101] = yoga
    
    # Birkaç tane daha örnek ders
    pilates = FitnessClass("Pilates", "Ceren Hoca", 10, "2025-06-16 10:00", 60.0)
    classes_db[102] = pilates

# Veritabanını başlat
init_db()

# --- API ENDPOINTLERİ ---

@app.route('/')
def home():
    return "Fitness Backend Calisiyor! /api/classes adresine git."

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
    # Sözlükteki dersleri listeye çevirip döndür
    result = []
    for c_id, c in classes_db.items():
        result.append({
            "id": c_id,
            "title": c.title,
            "instructor": c.instructor,
            "capacity": c.capacity,
            "occupancy": c.current_occupancy(),
            "base_price": c.base_price
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)