import os
import requests

# GitHub Secrets
TOKEN = os.getenv("INSTAGRAM_TOKEN")
USER_ID = os.getenv("INSTAGRAM_USER_ID")

def karesel_test_gonder():
    print("--- Bot Baslatildi ---")
    
    # Instagram'in kesin kabul edecegi KARE (1:1) bir test resmi
    # Bu resim Instagram standartlarina uygundur.
    test_image = "https://picsum.photos/1080/1080" 
    
    # 1. Adim: Media Container Olustur
    url = f"https://graph.facebook.com/v21.0/{USER_ID}/media"
    payload = {
        'image_url': test_image,
        'caption': 'Bingöl için ilk otomatik paylaşım! 🚀 #bingol #altinfiyatlari',
        'access_token': TOKEN
    }
    
    print("1. Adim: Kare resim gonderiliyor...")
    r = requests.post(url, data=payload)
    result = r.json()
    
    if 'id' in result:
        creation_id = result['id']
        # 2. Adim: Yayimla
        publish_url = f"https://graph.facebook.com/v21.0/{USER_ID}/media_publish"
        publish_payload = {
            'creation_id': creation_id,
            'access_token': TOKEN
        }
        print("2. Adim: Yayimlaniyor...")
        r_pub = requests.post(publish_url, data=publish_payload)
        print(f"TEBRIKLER! Yayin Sonucu: {r_pub.json()}")
    else:
        print(f"HATA DETAYI: {result}")

karesel_test_gonder()
