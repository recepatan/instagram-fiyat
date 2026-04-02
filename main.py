from __future__ import annotations
import os
import requests
import io
import time
import random
import datetime
from PIL import Image, ImageDraw, ImageFont
from instagrapi import Client

# --- YAPILANDIRMA ---
INSTA_USER = os.getenv("INSTA_USER")
INSTA_PASS = os.getenv("INSTA_PASS")
API_URL = "https://ayarlar.bingolder.com/sarrafiye"
IMG_URL = "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgcggkTkb6pDpnXjCcgKCqh9qRXA-g9NY0gpI4cvjgKF3YMuEjU6DB6EUKEaCx8QYZZHMZP80mbL4HvQWxumtsaG9EL_q4g8AlB9S-rjFvpPf6nxm5Z0EIMKtRMSh2C7lD4jIzx9xWhjmRgple455pw7ozEIlQLDwPbp_6bbwhxEFPtqDN-GGHrzXHcFATe/s1408/30622.png"

def get_gold_data():
    try:
        response = requests.get(API_URL, timeout=15)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return None

def create_price_image(data):
    try:
        response = requests.get(IMG_URL, timeout=20)
        img = Image.open(io.BytesIO(response.content))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 35)
        except:
            font = ImageFont.load_default()

        coords = {
            "gram24": (365, 520, 155),
            "ceyrek": (365, 520, 260),
            "yarim":  (365, 520, 365),
            "tam":    (365, 520, 470),
            "ata":    (365, 520, 580),
            "bilezik":(365, 520, 690),
            "ons":    (365, 520, 800)
        }

        for key, pos in coords.items():
            alis = str(data.get(f"{key}_alis", "0"))
            satis = str(data.get(f"{key}_satis", "0"))
            draw.text((pos[0], pos[2]), alis, font=font, fill=(60, 60, 60))
            draw.text((pos[1], pos[2]), satis, font=font, fill=(60, 60, 60))

        tarih = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        draw.text((800, 930), tarih, font=font, fill=(100, 100, 100))

        img.save("paylasim.jpg")
        return True
    except Exception as e:
        print(f"Görsel oluşturma hatası: {e}")
        return False

def upload_to_instagram():
    cl = Client()
    
    # IP Engelini Aşmak İçin Farklı Bir Cihaz Kimliği (iPhone 13)
    cl.set_user_agent("Instagram 219.0.0.12.117 (iPhone13,4; iOS 15_0_2; en_US; en-US; scale=3.00; 1170x2532; 329153541)")

    try:
        print("Instagram'a giriş denemesi yapılıyor...")
        # Rastgele uzun bekleme (IP engeli için kritik)
        time.sleep(random.randint(15, 30))
        
        cl.login(INSTA_USER, INSTA_PASS)
        
        time.sleep(random.randint(5, 10)) # Giriş sonrası bekle
        
        caption = f"Bingöl Güncel Altın Fiyatları ({datetime.datetime.now().strftime('%d.%m.%Y')}) #bingöl #altın #kuyumcu"
        cl.photo_upload("paylasim.jpg", caption)
        print("BAŞARILI: Görsel paylaşıldı.")
        
    except Exception as e:
        error_msg = str(e)
        if "challenge_required" in error_msg:
            print("HATA: Instagram doğrulama kodu istiyor. E-postanızı kontrol edin ve onaylayın.")
        elif "feedback_required" in error_msg:
            print("HATA: IP adresi engellendi. Lütfen 24 saat bekleyin veya manuel onay verin.")
        else:
            print(f"Instagram Hatası: {error_msg}")

if __name__ == "__main__":
    fiyatlar = get_gold_data()
    if fiyatlar and create_price_image(fiyatlar):
        upload_to_instagram()
