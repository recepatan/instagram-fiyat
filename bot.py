import os
import requests

# GitHub Secrets'tan gelen bilgiler
TOKEN = os.getenv("INSTAGRAM_TOKEN")
USER_ID = os.getenv("INSTAGRAM_USER_ID")

def test_run():
    print("--- Bot Baslatildi ---")
    print(f"Hedef ID: {USER_ID}")
    
    # ImgBB kismini atlayip direkt bir test resmi gonderelim (Google logosu gibi)
    test_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/1200px-Google_2015_logo.svg.png"
    
    # 1. Adim: Media Container Olustur
    url = f"https://graph.facebook.com/v21.0/{USER_ID}/media"
    payload = {
        'image_url': test_image,
        'caption': 'Bingöl Altın Fiyatları Bot Testi 🚀',
        'access_token': TOKEN
    }
    
    print("1. Adim: Instagram'a resim gonderiliyor...")
    r = requests.post(url, data=payload)
    result = r.json()
    print(f"Gelen Cevap: {result}")

    if 'id' in result:
        creation_id = result['id']
        # 2. Adim: Yayimla
        publish_url = f"https://graph.facebook.com/v21.0/{USER_ID}/media_publish"
        publish_payload = {
            'creation_id': creation_id,
            'access_token': TOKEN
        }
        print("2. Adim: Resim yayimlaniyor...")
        r_pub = requests.post(publish_url, data=publish_payload)
        print(f"Yayin Sonucu: {r_pub.json()}")
    else:
        print("HATA: Resim yuklenemedi. Token veya ID hatali olabilir.")

test_run()
