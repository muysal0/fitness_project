import random
from locust import HttpUser, task, between

class FitnessUser(HttpUser):
    wait_time = between(1, 3)
    valid_class_ids = []

    def on_start(self):
        # Test başında dersleri öğrenelim
        with self.client.get("/api/classes", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                self.valid_class_ids = [c["id"] for c in data["classes"]]
            else:
                self.valid_class_ids = []

    @task(3)
    def view_classes(self):
        self.client.get("/api/classes")

    @task(1)
    def make_reservation(self):
        if not self.valid_class_ids:
            return

        class_id = random.choice(self.valid_class_ids)
        member_id = random.randint(100, 1000) # Geniş bir aralık verelim
        
        payload = {
            "member_id": member_id,
            "class_id": class_id
        }
        
        with self.client.post("/api/reservations", json=payload, name="Rezervasyon Yap", catch_response=True) as response:
            if response.status_code == 201:
                response.success() # Kayıt Başarılı
            
            elif response.status_code == 400:
                # 400 HATALARI ANALİZİ:
                # 1. "Zaten kayıtlı" -> Başarılı (Çifte kayıt engellendi)
                # 2. "full" veya "dolu" -> Başarılı (Kapasite kontrolü çalıştı)
                error_msg = response.json().get("error", "")
                
                # --- GÜNCELLENEN KISIM ---
                if "Zaten" in error_msg or "dolu" in error_msg.lower() or "full" in error_msg.lower():
                    response.success()
                else:
                    # Başka bir 400 hatasıysa (örn: geçersiz ID) gerçekten hatadır.
                    response.failure(f"Beklenmeyen 400 Hatası: {error_msg}")
            
            elif response.status_code == 400:
                error_msg = response.json().get("error", "")
                
                # Hem Türkçe hem İngilizce hata mesajlarını kabul ediyoruz
                if "Zaten" in error_msg or \
                   "dolu" in error_msg.lower() or \
                   "full" in error_msg.lower() or \
                   "already booked" in error_msg.lower():  # <--- YENİ EKLENEN
                    response.success()
                else:
                    response.failure(f"Beklenmeyen 400 Hatası: {error_msg}")