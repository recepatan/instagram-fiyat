import os
import requests

# GitHub Secrets
TOKEN = os.getenv("INSTAGRAM_TOKEN")
USER_ID = os.getenv("INSTAGRAM_USER_ID")

def kesin_cozum_testi():
    print("--- Bot Baslatildi ---")
    
    # Instagram'in asla reddedemeyecegi, dogrudan ham resim linki
    # Bu resim standart bir JPG'dir ve her yerden erisilebilir.
    test_image = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png" 
    
    # 1. Adim: Media Container Olustur
    url = f"https://graph.facebook.com/v21.0/{USER_ID}/media"
    payload = {
        'image_url': test_image,
        'caption': 'Sistem Testi: Bingöl Emlak Otomasyonu Hazır! ✅',
        'access_token': TOKEN
    }
    
    print(f"1. Adim: Resim yukleniyor ({test_image})...")
    r = requests.post(url, data=payload)
    result = r.json()
    
    if 'id' in result:
        creation_id = result['id']
        print(f"Basarili! Konteyner ID: {creation_id}")
        
        # 2. Adim: Yayimla
        publish_url = f"https://graph.facebook.com/v21.0/{USER_ID}/media_publish"
        publish_payload = {
            'creation_id': creation_id,
            'access_token': TOKEN
        }
        print("2. Adim: Instagram sayfasinda yayimlaniyor...")
        r_pub = requests.post(publish_url, data=publish_payload)
        print(f"FINAL SONUCU: {r_pub.json()}")
    else:
        print(f"INSTAGRAM HATASI: {result}")

kesin_cozum_testi()
