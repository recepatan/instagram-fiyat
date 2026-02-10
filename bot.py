import requests
import os
import pytz
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from instagrapi import Client

# 1. Veri Çekme ve Hesaplama
def get_gold_data():
    url = "https://ayarlar.bingolder.com/"
    try:
        response = requests.get(url, timeout=10)
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
        print(f"Hata: {e}")
        return None

def yuvarla(sayi):
    return int(round(sayi / 5.0) * 5)

# 2. Görsel Oluşturma
def create_post_image(fiyatlar):
    width, height = 1080, 1350 # Instagram Portre Modu (Daha çok yer kaplar)
    image = Image.new('RGB', (width, height), color='#1a1a1a') # Koyu tema
    draw = ImageDraw.Draw(image)
    
    istanbul_tz = pytz.timezone('Europe/Istanbul')
    tarih_str = datetime.now(istanbul_tz).strftime("%d.%m.%Y - %H:%M")

    # Font ayarları (Sistemde font yoksa default'a düşer)
    try:
        header_font = ImageFont.truetype("arial.ttf", 55)
        price_font = ImageFont.truetype("arial.ttf", 42)
        info_font = ImageFont.truetype("arial.ttf", 30)
    except:
        header_font = ImageFont.load_default()
        price_font = ImageFont.load_default()
        info_font = ImageFont.load_default()

    # Başlık ve Alt Başlık
    draw.text((60, 60), "BİNGÖL GÜNCEL ALTIN FİYATLARI", fill="#D4AF37", font=header_font)
    draw.text((60, 130), f"Güncelleme: {tarih_str}", fill="#aaaaaa", font=info_font)

    # Tam Liste Optimizasyonu
    kur_satis = fiyatlar['kur']['satis']
    isimlendirme = [
        ("has", "Çekme Altın (0,995)"),
        ("tel", "22 Ayar Bilezik"),
        ("ons", "ONS (USD)"),
        ("ata", "Ata Lira"),
        ("ziynet", "Ziynet Altın"),
        ("yarım", "Yarım Altın"),
        ("ceyrek", "Çeyrek Altın"),
        ("gram²⁴", "24 Ayar Gram"),
        ("besli", "Beşli Ata"),
        ("r.yarım", "Reşat Yarım"),
        ("r.çeyrek", "Reşat Çeyrek"),
        ("ondort", "14 Ayar Altın")
    ]

    y = 230
    for anahtar, gorunur_ad in isimlendirme:
        if anahtar in fiyatlar:
            val = fiyatlar[anahtar]
            # Ons ve Kur doğrudan yazılır, diğerleri Bingöl katsayısı ile çarpılır
            satis = int(val['satis']) if anahtar in ["kur", "ons"] else yuvarla(kur_satis * val['satis'])
            
            # Satır Tasarımı
            draw.text((60, y), gorunur_ad, fill="white", font=price_font)
            draw.text((780, y), f"{satis:,} TL".replace(",", "."), fill="#D4AF37", font=price_font)
            draw.line((60, y + 65, 1020, y + 65), fill="#333333", width=1)
            y += 85

    # Footer
    draw.text((60, height - 80), "Kaynak: bingolder.com", fill="#666666", font=info_font)
    
    image.save("insta_final.jpg")
    return "insta_final.jpg"

# 3. Instagram Yükleme
def upload_to_instagram(img_path):
    # GitHub Secrets'tan alınacak değerler
    USER = os.getenv('INSTA_USER')
    PASS = os.getenv('INSTA_PASS')
    
    if not USER or not PASS:
        print("HATA: Instagram kullanıcı bilgileri bulunamadı!")
        return

    cl = Client()
    try:
        # Şüpheli giriş uyarısını azaltmak için basit bir bekleme ve ayar
        cl.login(USER, PASS)
        cl.photo_upload(img_path, "Bingöl güncel altın fiyatları verileridir. 🚀\n\n#bingöl #altın #kuyumcu #bingolder")
        print("Instagram paylaşımı tamamlandı!")
    except Exception as e:
        print(f"Instagram Paylaşım Hatası: {e}")

if __name__ == "__main__":
    gold_data = get_gold_data()
    if gold_data:
        file = create_post_image(gold_data)
        upload_to_instagram(file)
