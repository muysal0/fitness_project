# 1. Python 3.9 Slim sürümünü kullan
FROM python:3.9-slim

# 2. Çalışma dizinini ayarla
WORKDIR /app

# 3. Gereksinim dosyasını kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Tüm proje dosyalarını kopyala
COPY . .

# 5. Python'un 'src' klasörünü ana modül olarak görmesini sağla
ENV PYTHONPATH=/app

# 6. Flask'ın environment değişkenlerini ayarla (Önemli!)
ENV FLASK_APP=src/app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 7. Portu aç
EXPOSE 5000

# 8. Uygulamayı modül olarak başlat (Doğrusu budur)
CMD ["python", "-m", "src.app"]