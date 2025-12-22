import os
import shutil
import subprocess
import sys
import time

TARGET_FILE = "src/app.py"
BACKUP_FILE = "src/app.py.bak"

MUTANTS = [
    # --- PRICING (Helper Function İçinde) ---
    {
        "id": 1,
        "description": "Öğrenci indirimini %50'den %10'a düşür",
        "original": "price = price * 0.50",
        "mutation": "price = price * 0.90",
        "target": "test_check_student_discount"
    },
    {
        "id": 2,
        "description": "Öğrenci indirim mantığını tersine çevir",
        "original": "price = price * 0.50",
        "mutation": "price = price / 0.50",
        "target": "test_check_student_discount"
    },
    {
        "id": 3,
        "description": "Surge (Zam) oranını %20'den %0'a çek",
        "original": "price = price * 1.20",
        "mutation": "price = price * 1.00",
        "target": "test_check_surge_pricing"
    },
    {
        "id": 4,
        "description": "Surge (Zam) oranını aşırı artır (%50 yap)",
        "original": "price = price * 1.20",
        "mutation": "price = price * 1.50",
        "target": "test_check_surge_pricing"
    },
    {
        "id": 5,
        "description": "Doluluk eşiğini %80'den %99'a çıkar",
        "original": "if occupancy_rate > 0.80:",
        "mutation": "if occupancy_rate > 0.99:",
        "target": "test_surge_pricing_boundaries"
    },
    {
        "id": 6,
        "description": "Doluluk eşiğini %10'a düşür",
        "original": "if occupancy_rate > 0.80:",
        "mutation": "if occupancy_rate > 0.10:",
        "target": "test_surge_pricing_boundaries"
    },
    {
        "id": 7,
        "description": "Fiyat yuvarlamayı kaldır",
        "original": "return round(price, 2)",
        "mutation": "return price",
        "target": "test_price_rounding"
    },
    
    # --- RESERVATION ---
    {
        "id": 8,
        "description": "Kapasite kontrolünü devre dışı bırak",
        "original": "if f_class.attendees.count() >= f_class.capacity:",
        "mutation": "if False:",
        "target": "test_capacity_limit"
    },
    {
        "id": 9,
        "description": "Kapasite sınırını bir kişi esnet (> yerine >=)",
        "original": "if f_class.attendees.count() >= f_class.capacity:",
        "mutation": "if f_class.attendees.count() > f_class.capacity:",
        "target": "test_capacity_limit"
    },
    {
        "id": 10,
        "description": "Çifte kayıt (Duplicate) kontrolünü kaldır",
        "original": "if f_class in member.classes:",
        "mutation": "if False:",
        "target": "test_api_make_reservation_duplicate"
    },
    {
        "id": 11,
        "description": "Ders bulunamama kontrolünü kaldır",
        "original": "if not f_class:",
        "mutation": "if False:",
        "target": "test_api_invalid_class"
    },
    
    # --- API RESPONSE ---
    {
        "id": 12,
        "description": "Başarılı kayıt kodunu 201'den 200'e çevir",
        "original": "return jsonify({\"message\": \"Kayit Basarili\"}), 201",
        "mutation": "return jsonify({\"message\": \"Kayit Basarili\"}), 200",
        "target": "test_api_make_reservation_success"
    },
    {
        "id": 13,
        "description": "Liste çekerken kapasite bilgisini gizle",
        "original": "\"capacity\": c.capacity,",
        "mutation": "\"capacity\": 0,",
        "target": "test_api_list_classes"
    },
    {
        "id": 14,
        "description": "Öğrenci parametresini okumayı boz (Hep false)",
        "original": "request.args.get('student') == 'true'",
        "mutation": "False",
        "target": "test_check_student_discount"
    },
    {
        "id": 15,
        "description": "Veritabanı bağlantı retry sayısını 5'ten 0'a düşür",
        "original": "retries -= 1",
        "mutation": "retries = 0",
        "target": "test_db_retry_logic"
    }
]

def run_mutation_tests():
    start_time = time.time()
    print("="*60)
    print("🚀 TURBO MUTASYON TESTİ (15/15)")
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
                total -= 1
                continue

            mutated_content = content.replace(mutant["original"], mutant["mutation"])
            with open(TARGET_FILE, "w", encoding="utf-8") as f:
                f.write(mutated_content)

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

    print("-" * 60)
    if total > 0:
        print(f"📊 SKOR: {score}/{total} ({(score/total)*100:.1f}%)")
    else:
        print("📊 Test edilemedi.")
    print("="*60)

if __name__ == "__main__":
    run_mutation_tests()