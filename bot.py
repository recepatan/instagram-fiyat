import requests
import os
import pytz
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from instagrapi import Client

# 1. Veri Çekme ve Hesaplama Fonksiyonu
def get_gold_data():
    url = "https://ayarlar.bingolder.com/"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        rows = data.get('values', [])
        if not rows:
            print("Veri bulunamadı.")
            return None

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

# 2. Görsel Oluşturma Fonksiyonu
def create_post_image(fiyatlar):
    width, height = 1080, 1350
    # Şık Koyu Lacivert/Siyah Arka Plan
    image = Image.new('RGB', (width, height), color='#0f172a') 
    draw = ImageDraw.Draw(image)
    
    istanbul_tz = pytz.timezone('Europe/Istanbul')
    tarih_str = datetime.now(istanbul_tz).strftime("%d.%m.%Y - %H:%M")

    # Font Ayarı (GitHub Sunucularında hata vermemesi için korumalı)
    try:
        # Sunucuda varsa bu fontları kullanır
        header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        price_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    except:
        # Yoksa standart fonta döner
        header_font = ImageFont.load_default()
        price_font = ImageFont.load_default()

    # Başlık Alanı
    draw.rectangle([0, 0, width, 200], fill='#1e293b') # Üst bant
    draw.text((60, 50), "BİNGÖL GÜNCEL ALTIN FİYATLARI", fill="#ffb300", font=header_font)
    draw.text((60, 130), f"Son Güncelleme: {tarih_str}", fill="#94a3b8", font=price_font)

    # Ürün Listesi
    kur_satis = fiyatlar['kur']['satis']
    isimlendirme = [
        ("has", "Has Altın (24 Ayar)"),
        ("tel", "22 Ayar Bilezik"),
        ("ata", "Ata Lira"),
        ("ziynet", "Ziynet Altın"),
        ("yarım", "Yarım Altın"),
        ("ceyrek", "Çeyrek Altın"),
        ("gram²⁴", "24 Ayar Gram"),
        ("ons", "ONS (Dolar)"),
        ("ondort", "14 Ayar Altın")
    ]

    y = 280
    for anahtar, gorunur_ad in isimlendirme:
        if anahtar in fiyatlar:
            val = fiyatlar[anahtar]
            # Ons ise direkt yaz, değilse Bingöl katsayısıyla hesapla
            f_satis = int(val['satis']) if anahtar == "ons" else yuvarla(kur_satis * val['satis'])
            
            # Satır Tasarımı (Hizalama)
            draw.text((80, y), gorunur_ad, fill="white", font=price_font)
            draw.text((750, y), f"{f_satis:,} TL".replace(",", "."), fill="#ffb300", font=price_font)
            
            # Alt çizgi
            draw.line((80, y + 70, 1000, y + 70), fill="#334155", width=2)
            y += 105

    # Alt Bilgi (Footer)
    draw.text((80, height - 100), "Veriler: bingolder.com", fill="#475569", font=price_font)
    
    img_name = "insta_post.jpg"
    image.save(img_name, quality=95)
    return img_name

# 3. Instagram'a Yükleme Fonksiyonu
def upload_to_instagram(img_path):
    USER = os.getenv('INSTA_USER')
    PASS = os.getenv('INSTA_PASS')
    
    if not USER or not PASS:
        print("HATA: Secrets ayarları yapılmamış!")
        return

    cl = Client()
    # GitHub üzerinden girişte "Challenge" takılmasını önlemek için ayarlar
    cl.delay_range = [2, 5] 
    
    try:
        print(f"{USER} kullanıcısı ile giriş yapılıyor...")
        cl.login(USER, PASS)
        
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
    else:
        print("Veri çekilemediği için işlem iptal edildi.")
