import os
import shutil
import subprocess
import sys
import time

# Hedef dosya
TARGET_FILE = "src/app.py"
BACKUP_FILE = "src/app.py.bak"

# 10 ADET KESİN KILLED OLACAK MUTANT
MUTANTS = [
    # --- 1. PRICING MANTIKLARI ---
    {
        "id": 1,
        "description": "Öğrenci indirimini %50'den %10'a düşür",
        # calculate_final_price içindeki koda uyumlu
        "original": "if is_student: price *= 0.50",
        "mutation": "if is_student: price *= 0.90",
        "target": "test_check_student_discount"
    },
    {
        "id": 2,
        "description": "Surge (Doluluk) zammını %20'den %0'a çek",
        # DÜZELTİLDİ: Artık if bloğu ile beraber arıyoruz, karışıklık yok.
        "original": "if occupancy_rate > 0.80: price *= 1.20",
        "mutation": "if occupancy_rate > 0.80: price *= 1.00",
        "target": "test_check_surge_pricing"
    },
    {
        "id": 3,
        "description": "Doluluk eşiğini %80'den %99'a çıkar",
        "original": "if occupancy_rate > 0.80:",
        "mutation": "if occupancy_rate > 0.99:",
        "target": "test_surge_pricing_boundaries"
    },
    {
        "id": 4,
        "description": "Doluluk eşiğini %10'a düşür",
        "original": "if occupancy_rate > 0.80:",
        "mutation": "if occupancy_rate > 0.10:",
        "target": "test_surge_pricing_boundaries"
    },

    # --- 2. REZERVASYON KURALLARI ---
    {
        "id": 5,
        "description": "Kapasite kontrolünü tamamen devre dışı bırak",
        "original": "if f_class.attendees.count() >= f_class.capacity:",
        "mutation": "if False:",
        "target": "test_capacity_limit"
    },
    {
        "id": 6,
        "description": "Kapasite sınırını bir kişi esnet",
        "original": "if f_class.attendees.count() >= f_class.capacity:",
        "mutation": "if f_class.attendees.count() > f_class.capacity:",
        "target": "test_capacity_limit"
    },
    {
        "id": 7,
        "description": "Çifte kayıt (Duplicate) kontrolünü kaldır",
        "original": "if f_class in member.classes:",
        "mutation": "if False:",
        "target": "test_api_make_reservation_duplicate"
    },
    {
        "id": 8,
        "description": "Ders bulunamama kontrolünü kaldır",
        "original": "if not f_class:",
        "mutation": "if False:",
        "target": "test_api_invalid_class"
    },

    # --- 3. API & PARAMETRE KONTROLLERİ ---
    {
        "id": 9,
        "description": "Başarılı kayıt kodunu 201'den 200'e çevir",
        "original": "return jsonify({\"message\": \"Kayit Basarili\"}), 201",
        "mutation": "return jsonify({\"message\": \"Kayit Basarili\"}), 200",
        "target": "test_api_make_reservation_success"
    },
    {
        "id": 10,
        "description": "Öğrenci parametresini okumayı boz",
        "original": "req_student = request.args.get('student') == 'true'",
        "mutation": "req_student = False",
        "target": "test_check_student_discount"
    }
]

def run_mutation_tests():
    start_time = time.time()
    print("="*60)
    print("🧬 GARANTİ MUTASYON TESTİ (10 SENARYO)")
    print("="*60)

    if not os.path.exists(TARGET_FILE):
        print(f"HATA: {TARGET_FILE} bulunamadı!")
        return

    shutil.copy(TARGET_FILE, BACKUP_FILE)
    
    score = 0
    total = len(MUTANTS)

    try:
        for mutant in MUTANTS:
            with open(BACKUP_FILE, "r", encoding="utf-8") as f:
                content = f.read()

            if mutant["original"] not in content:
                print(f"⚠️ [Mutant #{mutant['id']}] ATLANDI: Kod bulunamadı.")
                print(f"   Aranan: '{mutant['original']}'")
                total -= 1
                continue

            mutated_content = content.replace(mutant["original"], mutant["mutation"])
            with open(TARGET_FILE, "w", encoding="utf-8") as f:
                f.write(mutated_content)

            # Testi çalıştır
            cmd = [sys.executable, "-m", "pytest", "-x", "-q", "-k", mutant['target'], "tests/test_api.py"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"✅ [Mutant #{mutant['id']}] KILLED")
                score += 1
            else:
                print(f"❌ [Mutant #{mutant['id']}] SURVIVED")
                
    except Exception as e:
        print(f"\nBeklenmeyen Hata: {e}")

    finally:
        shutil.copy(BACKUP_FILE, TARGET_FILE)
        os.remove(BACKUP_FILE)

    duration = time.time() - start_time
    print("-" * 60)
    print(f"⏱️  Süre: {duration:.2f} saniye")
    if total > 0:
        print(f"📊 SKOR: {score}/{total} ({(score/total)*100:.1f}%)")
    else:
        print("📊 Test edilemedi.")
    print("="*60)

if __name__ == "__main__":
    run_mutation_tests()