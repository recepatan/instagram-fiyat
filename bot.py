import requests
import os
import json
from datetime import datetime
import pytz
from PIL import Image, ImageDraw, ImageFont

# 1. Veri Çekme Fonksiyonu
def get_gold_data():
    url = "https://ayarlar.bingolder.com/"
    response = requests.get(url)
    data = response.json()
    rows = data.get('values', [])
    
    # Sadece göstermek istediğimiz ürünler
    mapping = {
        "has": "Has Altın",
        "ceyrek": "Çeyrek Altın",
        "yarım": "Yarım Altın",
        "ata": "Ata Lira",
        "tel": "22 Ayar Bilezik"
    }
    
    results = []
    # Kur bilgisini al (hesaplama için)
    kur = float(str(rows[1][1]).replace(',', '.'))
    
    for row in rows[1:]:
        key = row[0].strip().lower()
        if key in mapping:
            satis = float(str(row[2]).replace(',', '.'))
            # Has/Kur hariç diğerlerini kurla çarpıp 5'e yuvarla
            fiyat = int(round((satis * kur) / 5.0) * 5) if key != "kur" else int(satis)
            results.append(f"{mapping[key]}: {fiyat:,} TL")
    
    return results

# 2. Görsel Oluşturma (Instagram için Kare Resim)
def create_image(prices):
    img = Image.new('RGB', (1080, 1080), color='#1a1a1a') # Koyu arka plan
    draw = ImageDraw.Draw(img)
    
    # Not: GitHub Actions'ta standart font kullanacağız
    try:
        font_title = ImageFont.load_default() # Daha iyi görünüm için .ttf dosyası eklenebilir
    except:
        font_title = ImageFont.load_default()

    draw.text((100, 100), "BİNGÖL KUYUMCULAR DERNEĞİ", fill='#D4AF37')
    draw.text((100, 160), datetime.now(pytz.timezone('Europe/Istanbul')).strftime("%d.%m.%Y %H:%M"), fill='white')
    
    y_pos = 300
    for p in prices:
        draw.text((100, y_pos), p, fill='#D4AF37')
        y_pos += 80
        
    img.save('gunluk_altin.jpg')

# 3. Instagram API Paylaşımı
def post_to_instagram():
    # Bu değişkenleri GitHub Secrets'a ekleyeceksiniz
    ACCESS_TOKEN = os.getenv('INSTAGRAM_TOKEN')
    IG_USER_ID = os.getenv('INSTAGRAM_USER_ID')
    IMAGE_URL = "RESIM_URL_BURAYA_GELECEK" # Önemli Not: Aşağıya bakın

    # Not: Instagram API görselin internette bir URL'de olmasını ister. 
    # Alternatif: Imgur API veya GitHub Pages üzerinden geçici URL üretilebilir.
    # Şimdilik mantığı kuruyoruz:
    print("Görsel oluşturuldu, API gönderimi tetikleniyor...")

if __name__ == "__main__":
    prices = get_gold_data()
    create_image(prices)
    # post_to_instagram() # API ayarlarınız bitince aktif edilecek
