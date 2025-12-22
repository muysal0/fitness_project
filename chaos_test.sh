#!/bin/bash

echo "==========================================="
echo "🔥 CHAOS ENGINEERING TEST BAŞLIYOR 🔥"
echo "==========================================="

# 1. Her şeyin çalıştığından emin ol
echo "[1] Sistem kontrol ediliyor..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/classes | grep 200 > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Sistem şu an sağlıklı çalışıyor."
else
    echo "❌ Sistem zaten bozuk! Önce 'docker-compose up' yap."
    exit 1
fi

# 2. KAOS: Veritabanını Öldür!
echo "-------------------------------------------"
echo "[2] 💣 KAOS ZAMANI: Veritabanı konteyneri durduruluyor..."
# Konteyner adını bulup durduruyoruz (fitness_final-db-1 veya benzeri olabilir)
DB_CONTAINER=$(docker ps | grep postgres | awk '{print $1}')
docker stop $DB_CONTAINER
echo "💀 Veritabanı durduruldu (ID: $DB_CONTAINER)."
sleep 10

# 3. GÖZLEM: Veritabanı yokken site ne yapıyor?
echo "-------------------------------------------"
echo "[3] 👀 GÖZLEM: API'ye istek atılıyor..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/classes)
RESPONSE=$(curl -s http://localhost:5000/api/classes)

echo "Gelen Yanıt Kodu: $HTTP_CODE"
if [ "$HTTP_CODE" == "503" ]; then
    echo "✅ BAŞARILI: Sistem çökmedi, '503 Service Unavailable' döndü."
    echo "Mesaj: $RESPONSE"
else
    echo "⚠️ BEKLENMEYEN DURUM: Sistem $HTTP_CODE döndü."
fi

# 4. İYİLEŞME: Veritabanını Geri Getir
echo "-------------------------------------------"
echo "[4] 🚑 İYİLEŞME: Veritabanı yeniden başlatılıyor..."
docker start $DB_CONTAINER
echo "⏳ Veritabanının açılması bekleniyor (5 saniye)..."
sleep 5

# 5. FİNAL KONTROL
echo "-------------------------------------------"
echo "[5] 🔄 KONTROL: API tekrar deneniyor..."
HTTP_CODE_FINAL=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/classes)

if [ "$HTTP_CODE_FINAL" == "200" ]; then
    echo "🎉 MÜKEMMEL! Sistem veritabanı gelince otomatik düzeldi (Self-Healing)."
else
    echo "❌ HATA: Sistem düzelmedi. Yanıt: $HTTP_CODE_FINAL"
fi

echo "==========================================="
echo "TEST TAMAMLANDI"