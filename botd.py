import requests
import os
import pytz
from datetime import datetime

# --- YARDIMCI FONKSİYONLAR ---
def yuvarla(sayi):
    try:
        return int(round(float(sayi) / 5.0) * 5)
    except:
        return 0

def instagram_metni_olustur(fiyatlar, isimlendirme, baslik, kur_alis, kur_satis):
    metin = f"📢 {baslik}\n"
    metin += f"⏰ Güncelleme: {datetime.now(pytz.timezone('Europe/Istanbul')).strftime('%H:%M')}\n\n"
    
    for anahtar, gorunur_ad in isimlendirme:
        if anahtar in fiyatlar:
            deger = fiyatlar[anahtar]
            if anahtar in ["kur", "ons"]:
                f_alis = int(deger['alis'])
                f_satis = int(deger['satis'])
            else:
                f_alis = yuvarla(kur_alis * deger['alis'])
                f_satis = yuvarla(kur_satis * deger['satis'])
            
            metin += f"🔸 {gorunur_ad}\n"
            metin += f"   Alış: {f_alis:,} TL | Satış: {f_satis:,} TL\n"
    
    metin += "\n📍 Bingöl Güncel Altın Fiyatları\n"
    metin += "#altın #altınfiyatları #bingöl #ekonomi #yatırım"
    return metin

def instagram_paylas(mesaj):
    TOKEN = os.getenv("INSTAGRAM_TOKEN")
    USER_ID = os.getenv("INSTAGRAM_USER_ID")
    # Sabit şık bir altın resmi veya Wikipedia resmi
    RESIM_URL = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
    
    try:
        url = f"https://graph.facebook.com/v21.0/{USER_ID}/media"
        payload = {'image_url': RESIM_URL, 'caption': mesaj, 'access_token': TOKEN}
        r = requests.post(url, data=payload)
        res = r.json()
        
        if 'id' in res:
            creation_id = res['id']
            publish_url = f"https://graph.facebook.com/v21.0/{USER_ID}/media_publish"
            publish_payload = {'creation_id': creation_id, 'access_token': TOKEN}
            r_pub = requests.post(publish_url, data=publish_payload)
            print(f"✅ Instagram Paylaşıldı: {r_pub.json()}")
        else:
            print(f"❌ Instagram Hatası: {res}")
    except Exception as e:
        print(f"⚠️ Instagram hatası: {e}")

# --- ANA AKIŞ ---
def run_bot():
    try:
        # 1. Veri Çekme
        url = "https://ayarlar.bingolder.com/"
        data = requests.get(url).json()
        rows = data.get('values', [])
        
        if not rows:
            print("⚠️ Veri çekilemedi.")
            return

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

        kur_alis = fiyatlar['kur']['alis']
        kur_satis = fiyatlar['kur']['satis']

        # 2. Ürün Listesi ve Başlık
        isimlendirme = [
            ("kur", "KUR"), ("has", "Çekme Altın (0,995)"), ("tel", "Burma Bilezik"),
            ("iscilikli", "İşçilikli Ürün"), ("ondort", "14 Ayar Altın"), 
            ("besli", "Beşli Ata"), ("ata", "Ata Lira"), ("ziynet", "Ziynet Altın"),
            ("yarım", "Yarım Altın"), ("ceyrek", "Çeyrek Altın"),
            ("gram²⁴", "Gram Altın (0,995)"), ("ons", "ONS (USD)")
        ]
        
        simdi = datetime.now(pytz.timezone('Europe/Istanbul'))
        baslik = f"{simdi.strftime('%d.%m.%Y')} Altın Fiyatları"

        # 3. Instagram Paylaşımı
        mesaj = instagram_metni_olustur(fiyatlar, isimlendirme, baslik, kur_alis, kur_satis)
        instagram_paylas(mesaj)

    except Exception as e:
        print(f"❌ HATA: {e}")

if __name__ == "__main__":
    run_bot()
