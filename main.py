from __future__ import annotations
import os
import requests
import io
from PIL import Image, ImageDraw, ImageFont
from instagrapi import Client
import datetime

# GitHub Secrets'dan verileri çekiyoruz
INSTA_USER = os.getenv("INSTA_USER")
INSTA_PASS = os.getenv("INSTA_PASS")
API_URL = "https://ayarlar.bingolder.com/sarrafiye"

def get_gold_data():
    try:
        response = requests.get(API_URL)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"API hatası: {e}")
        return None

def create_price_image(data):
    # Blogger üzerindeki görselin URL'si
    img_url = "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgcggkTkb6pDpnXjCcgKCqh9qRXA-g9NY0gpI4cvjgKF3YMuEjU6DB6EUKEaCx8QYZZHMZP80mbL4HvQWxumtsaG9EL_q4g8AlB9S-rjFvpPf6nxm5Z0EIMKtRMSh2C7lD4jIzx9xWhjmRgple455pw7ozEIlQLDwPbp_6bbwhxEFPtqDN-GGHrzXHcFATe/s1408/30622.png"
    
    try:
        # Görseli internetten indiriyoruz
        response = requests.get(img_url)
        response.raise_for_status()
        
        # BytesIO ile görseli bellekte açıyoruz
        img = Image.open(io.BytesIO(response.content))
        draw = ImageDraw.Draw(img)
        
        # Font ayarı
        try:
            # GitHub Actions (Ubuntu) üzerinde genellikle bu font bulunur
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 35)
        except:
            print("Özel font bulunamadı, varsayılan kullanılıyor.")
            font = ImageFont.load_default()

        # Koordinat haritası
        coords = {
            "gram24": (365, 520, 155),
            "ceyrek": (365, 520, 260),
            "yarim":  (365, 520, 365),
            "tam":    (365, 520, 470),
            "ata":    (365, 520, 580),
            "bilezik":(365, 520, 690),
            "ons":    (365, 520, 800)
        }

        # Verileri görsele yazdır
        for key, pos in coords.items():
            alis = str(data.get(f"{key}_alis", "0"))
            satis = str(data.get(f"{key}_satis", "0"))
            draw.text((pos[0], pos[2]), alis, font=font, fill=(60,60,60))
            draw.text((pos[1], pos[2]), satis, font=font, fill=(60,60,60))

        # Çıktıyı kaydet
        img.save("paylasim.jpg")
        print("Görsel başarıyla oluşturuldu.")
        return True
    except Exception as e:
        print(f"Görsel oluşturma hatası: {e}")
        return False

def upload():
    try:
        cl = Client()
        cl.login(INSTA_USER, INSTA_PASS)
        
        caption = f"Bingöl Güncel Altın Fiyatları - {datetime.datetime.now().strftime('%d.%m.%Y')}\n\n#bingöl #altın #çeyrekaltın #kuyumcu #bingolder"
        
        cl.photo_upload("paylasim.jpg", caption)
        print("Instagram paylaşımı başarılı!")
    except Exception as e:
        print(f"Instagram yükleme hatası: {e}")

if __name__ == "__main__":
    data = get_gold_data()
    if data:
        if create_price_image(data):
            upload()
