import requests
import os
import pytz
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from instagrapi import Client

# 1. Veri Çekme ve Hesaplama (Aynı kalıyor)
def get_gold_data():
    url = "https://ayarlar.bingolder.com/"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        rows = data.get('values', [])
        if not rows: return None

        fiyatlar = {}
        for row in rows[1:]:
            if len(row) >= 3:
                key = row[0].strip().lower()
                try:
                    fiyatlar[key] = {
                        'alis': float(str(row[1]).replace(',', '.')), 
                        'satis': float(str(row[2]).replace(',', '.'))
                    }
                except: continue
        return fiyatlar
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return None

def yuvarla(sayi):
    return int(round(sayi / 5.0) * 5)

# 2. Görsel Oluşturma (Aynı kalıyor)
def create_post_image(fiyatlar):
    width, height = 1080, 1350
    image = Image.new('RGB', (width, height), color='#0f172a') 
    draw = ImageDraw.Draw(image)
    
    istanbul_tz = pytz.timezone('Europe/Istanbul')
    tarih_str = datetime.now(istanbul_tz).strftime("%d.%m.%Y - %H:%M")

    try:
        header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        price_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    except:
        header_font = ImageFont.load_default()
        price_font = ImageFont.load_default()

    draw.rectangle([0, 0, width, 200], fill='#1e293b')
    draw.text((60, 50), "BİNGÖL GÜNCEL ALTIN FİYATLARI", fill="#ffb300", font=header_font)
    draw.text((60, 130), f"Son Güncelleme: {tarih_str}", fill="#94a3b8", font=price_font)

    kur_satis = fiyatlar['kur']['satis']
    isimlendirme = [
        ("has", "Has Altın (24 Ayar)"), ("tel", "22 Ayar Bilezik"),
        ("ata", "Ata Lira"), ("ziynet", "Ziynet Altın"),
        ("yarım", "Yarım Altın"), ("ceyrek", "Çeyrek Altın"),
        ("gram²⁴", "24 Ayar Gram"), ("ons", "ONS (Dolar)"),
        ("ondort", "14 Ayar Altın")
    ]

    y = 280
    for anahtar, gorunur_ad in isimlendirme:
        if anahtar in fiyatlar:
            val = fiyatlar[anahtar]
            f_satis = int(val['satis']) if anahtar == "ons" else yuvarla(kur_satis * val['satis'])
            draw.text((80, y), gorunur_ad, fill="white", font=price_font)
            draw.text((750, y), f"{f_satis:,} TL".replace(",", "."), fill="#ffb300", font=price_font)
            draw.line((80, y + 70, 1000, y + 70), fill="#334155", width=2)
            y += 105

    draw.text((80, height - 100), "Veriler: bingolder.com", fill="#475569", font=price_font)
    img_name = "insta_post.jpg"
    image.save(img_name, quality=95)
    return img_name

# 3. Instagram'a Yükleme (GÜNCELLENEN KISIM)
def upload_to_instagram(img_path):
    # GitHub Secrets üzerinden "INSTA_SESSIONID" adıyla alacağız
    SESSION_ID = os.getenv('INSTA_SESSIONID')
    
    if not SESSION_ID:
        print("HATA: INSTA_SESSIONID Secrets ayarı yapılmamış!")
        return

    cl = Client()
    
    try:
        print("Session ID ile giriş yapılıyor...")
        # Şifre gerektirmeyen, doğrudan tarayıcı oturumunu kullanan metod
        cl.login_by_sessionid(SESSION_ID)
        
        caption = (
            "Bingöl Güncel Altın Fiyatları 📊\n\n"
            "Veriler Bingöl Kuyumcular Derneği'nden otomatik alınmıştır.\n\n"
            "#bingöl #altınfiyatları #çeyrekaltın #ekonomi #bingolder"
        )
        
        cl.photo_upload(img_path, caption)
        print("Paylaşım başarıyla yapıldı!")
    except Exception as e:
        print(f"Instagram hatası: {e}")

if __name__ == "__main__":
    data = get_gold_data()
    if data:
        post_file = create_post_image(data)
        upload_to_instagram(post_file)
