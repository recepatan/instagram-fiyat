import time # En üste ekle

def instagram_paylas(mesaj):
    TOKEN = os.getenv("INSTAGRAM_TOKEN")
    USER_ID = os.getenv("INSTAGRAM_USER_ID")
    
    RESIM_URL = "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiNmhusZFfmgifFe2RqTOpxBA-nzIwWzMAGLRncBIfAR8WxVVZpd_dkyklfsQbtXPNZeR1nnZSQ6iK6RDcRmYSkWi4yMpVedtqsQgBes2zYz2CDWUOm3xmZv8lSRlgJec_Mvq_Xl5_Q9jXpwpVKgCZK6bkszL10kku_z8Ebi9JHrPWcGEZfgrzjBbXSmP8r/w410-h286-p-k-no-nu-rw/view-3d-golden-bee-Photoroom.png"
    
    try:
        # 1. Adım: Medya Hazırlama
        url = f"https://graph.facebook.com/v21.0/{USER_ID}/media"
        payload = {'image_url': RESIM_URL, 'caption': mesaj, 'access_token': TOKEN}
        r = requests.post(url, data=payload)
        res = r.json()
        
        if 'id' in res:
            creation_id = res['id']
            
            # --- KRİTİK NOKTA: BEKLEME ---
            print("⏳ Resim işleniyor, 10 saniye bekleniyor...")
            time.sleep(10) # Instagram'ın resmi indirmesi için süre tanıyoruz
            # -----------------------------
            
            # 2. Adım: Yayına Alma
            publish_url = f"https://graph.facebook.com/v21.0/{USER_ID}/media_publish"
            publish_payload = {'creation_id': creation_id, 'access_token': TOKEN}
            r_pub = requests.post(publish_url, data=publish_payload)
            
            final_res = r_pub.json()
            if 'id' in final_res:
                print(f"✅ Instagram Paylaşıldı! Post ID: {final_res['id']}")
            else:
                print(f"❌ Yayınlama Hatası: {final_res}")
        else:
            print(f"❌ Medya Hazırlama Hatası: {res}")
    except Exception as e:
        print(f"⚠️ Instagram hatası: {e}")
