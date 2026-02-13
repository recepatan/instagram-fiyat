import os
import requests

# GitHub Secrets
TOKEN = os.getenv("INSTAGRAM_TOKEN")
USER_ID = os.getenv("INSTAGRAM_USER_ID")

def final_test():
    print("--- Bot Baslatildi ---")
    
    # Instagram'in sevdigi, yonlendirme icermeyen dogrudan .jpg linki
    test_image = "https://i.ibb.co/XfR8vXn/test-image.jpg" 
    
    # 1. Adim: Media Container Olustur
    url = f"https://graph.facebook.com/v21.0/{USER_ID}/media"
    payload = {
        'image_url': test_image,
        'caption': 'Bingöl Emlak Otomasyon Sistemi Devreye Alındı! 🚀',
        'access_token': TOKEN
    }
    
    print("1. Adim: Instagram'a veri gonderiliyor...")
    r = requests.post(url, data=payload)
    result = r.json()
    
    if 'id' in result:
        creation_id = result['id']
        print(f"Konteyner Olustu ID: {creation_id}")
        
        # 2. Adim: Yayimla
        publish_url = f"https://graph.facebook.com/v21.0/{USER_ID}/media_publish"
        publish_payload = {
            'creation_id': creation_id,
            'access_token': TOKEN
        }
        print("2. Adim: Yayimlaniyor...")
        r_pub = requests.post(publish_url, data=publish_payload)
        print(f"SONUC: {r_pub.json()}")
    else:
        print(f"HATA ALINDI: {result}")

final_test()
