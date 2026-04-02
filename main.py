import os
import requests
from PIL import Image, ImageDraw, ImageFont
from instagrapi import Client
import datetime

# GitHub Secrets'dan verileri çekiyoruz
INSTA_USER = os.getenv("INSTA_USER")
INSTA_PASS = os.getenv("INSTA_PASS")
API_URL = "https://ayarlar.bingolder.com/sarrafiye"

def get_gold_data():
    response = requests.get(API_URL)
    return response.json() if response.status_code == 200 else None

def create_price_image(data):
    img = Image.open("https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgcggkTkb6pDpnXjCcgKCqh9qRXA-g9NY0gpI4cvjgKF3YMuEjU6DB6EUKEaCx8QYZZHMZP80mbL4HvQWxumtsaG9EL_q4g8AlB9S-rjFvpPf6nxm5Z0EIMKtRMSh2C7lD4jIzx9xWhjmRgple455pw7ozEIlQLDwPbp_6bbwhxEFPtqDN-GGHrzXHcFATe/s1408/30622.png")
    draw = ImageDraw.Draw(img)
    
    # Not: GitHub Actions üzerinde standart fontlar kısıtlıdır. 
    # 'DejaVuSans.ttf' genellikle Linux sunucularda bulunur.
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 35)
    except:
        font = ImageFont.load_default()

    # Koordinatları şablonunuza göre buraya girin
    # (Örnek: "ceyrek": (X_Alis, X_Satis, Y_Satir))
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
        draw.text((pos[0], pos[2]), str(data.get(f"{key}_alis", "0")), font=font, fill=(60,60,60))
        draw.text((pos[1], pos[2]), str(data.get(f"{key}_satis", "0")), font=font, fill=(60,60,60))

    img.save("paylasim.jpg")

def upload():
    cl = Client()
    cl.login(INSTA_USER, INSTA_PASS)
    cl.photo_upload("paylasim.jpg", "Bingöl Güncel Altın Fiyatları #bingöl #altın")

if __name__ == "__main__":
    data = get_gold_data()
    if data:
        create_price_image(data)
        upload()
      
