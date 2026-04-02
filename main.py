from __future__ import annotations
import os
import requests
import io
import time
import random
import datetime
from PIL import Image, ImageDraw, ImageFont
from instagrapi import Client

# --- YAPILANDIRMA (GitHub Secrets üzerinden gelir) ---
INSTA_USER = os.getenv("INSTA_USER")
INSTA_PASS = os.getenv("INSTA_PASS")
API_URL = "https://ayarlar.bingolder.com/sarrafiye"
# Blogger üzerindeki şablon görselinizin tam URL'si
IMG_URL = "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgcggkTkb6pDpnXjCcgKCqh9qRXA-g9NY0gpI4cvjgKF3YMuEjU6DB6EUKEaCx8QYZZHMZP80mbL4HvQWxumtsaG9EL_q4g8AlB9S-rjFvpPf6nxm5Z0EIMKtRMSh2C7lD4jIzx9xWhjmRgple455pw7ozEIlQLDwPbp_6bbwhxEFPtqDN-GGHrzXHcFATe/s1408/30622.png"

def get_gold_data():
    """API'den güncel fiyat verilerini çeker."""
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
        print(f"API Hatası: Durum Kodu {response.status_code}")
        return None
    except Exception as e:
        print(f"Veri çekme sırasında hata: {e}")
        return None

def create_price_image(data):
    """Blogger görselini indirir, üzerine fiyatları yazar ve kaydeder."""
    try:
        # Görseli internetten indir
        img_res = requests.get(IMG_URL, timeout=15)
        img_res.raise_for_status()
        
        # Bellekte görseli aç
        img = Image.open(io.BytesIO(img_res.content))
        draw = ImageDraw.Draw(img)
        
        # Font Ayarı (GitHub Ubuntu sunucularındaki standart yol)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 35)
        except:
            print("Özel font bulunamadı, varsayılan kullanılıyor.")
            font = ImageFont.load_default()

        # Koordinat Haritası (Alış X, Satış X, Satır Y)
        # Bu değerleri şablonun kutucuklarına göre ince ayar yapabilirsiniz
        coords = {
            "gram24": (365, 520, 155),
            "ceyrek": (365, 520, 260),
            "yarim":  (365, 520, 365),
            "tam":    (365, 520, 470),
            "ata":    (365, 520, 580),
            "bilezik":(365, 520, 690),
            "ons":    (365, 520, 800)
        }

        # Verileri yazdır
        for key, pos in coords.items():
            alis = str(data.get(f"{key}_alis", "0"))
            satis = str(data.get(f"{key}_satis", "0"))
            # Alış fiyatı
            draw.text((pos[0], pos[2]), alis, font=font, fill=(60, 60, 60))
            # Satış fiyatı
            draw.text((pos[1], pos[2]), satis, font=font, fill=(60, 60, 60))

        # Tarih damgası ekle (Opsiyonel)
        tarih_metni = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        draw.text((800, 930), tarih_metni, font=font, fill=(100, 100, 100))

        # Çıktıyı kaydet
        img.save("paylasim.jpg")
        print("Görsel (paylasim.jpg) başarıyla oluşturuldu.")
        return True
    except Exception as e:
        print(f"Görsel oluşturma hatası: {e}")
        return False

def upload_to_instagram():
    """Instagram'a giriş yapar ve görseli paylaşır."""
    try:
        cl = Client()
        # Şüpheli giriş uyarısını azaltmak için Samsung S10 simülasyonu
        cl.set_user_agent("Instagram 219.0.0.12.117 Android (29/10; 480dpi; 1080x2220; Samsung; SM-G973F; exynos9820; en_US; 340573356)")
        
        print("Instagram'a giriş yapılıyor...")
        # İnsan davranışını taklit etmek için rastgele bekleme
        time.sleep(random.randint(5, 12))
        
        cl.login(INSTA_USER, INSTA_PASS)
        
        # Paylaşım açıklaması
        caption = (
            f"Bingöl Güncel Altın Fiyatları 🏷️\n"
            f"Tarih: {datetime.datetime.now().strftime('%d.%m.%Y')}\n\n"
            f"Anlık fiyat takibi için: bingolder.com\n\n"
            f"#bingöl #altın #fiyatları #çeyrekaltın #kuyumcu #bingölkuyumcular"
        )
        
        # Fotoğrafı yükle
        cl.photo_upload("paylasim.jpg", caption)
        print("Instagram paylaşımı BAŞARILI!")
        
    except Exception as e:
        print(f"Instagram Hatası: {e}")
        print("Lütfen telefonunuzdan 'Giriş Yapan Bendim' onayını kontrol edin.")

if __name__ == "__main__":
    # 1. Veriyi çek
    fiyatlar = get_gold_data()
    
    if fiyatlar:
        # 2. Görseli hazırla
        if create_price_image(fiyatlar):
            # 3. Instagram'da paylaş
            upload_to_instagram()
    else:
        print("API'den veri alınamadığı için işlem durduruldu.")
