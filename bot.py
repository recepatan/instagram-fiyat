import requests
import os
import json
import pytz
import sys
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

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
    RESIM_URL = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
    
    if not TOKEN or not USER_ID:
        print("⚠️ Instagram bilgileri eksik, paylaşım yapılmadı.")
        return

    try:
        url = f"https://graph.facebook.com/v21.0/{USER_ID}/media"
        payload = {'image_url': RESIM_URL, 'caption': mesaj, 'access_token': TOKEN}
        r = requests.post(url, data=payload)
        res = r.json()
        
        if 'id' in res:
            creation_id = res['id']
            publish_url = f"https://graph.facebook.com/v21.0/{USER_ID}/media_publish"
            publish_payload = {'creation_id': creation_id, 'access_token': TOKEN}
            requests.post(publish_url, data=publish_payload)
            print("✅ Instagram paylaşımı başarılı!")
        else:
            print(f"❌ Instagram Hatası: {res}")
    except Exception as e:
        print(f"⚠️ Instagram fonksiyon hatası: {e}")

# --- ANA AKIŞ ---
def run_bot():
    try:
        # 1. Yetkilendirme Kontrolü
        blogger_token_raw = os.getenv('BLOGGER_TOKEN')
        if not blogger_token_raw:
            print("❌ HATA: BLOGGER_TOKEN bulunamadı!")
            return

        try:
            token_data = json.loads(blogger_token_raw)
            creds = Credentials.from_authorized_user_info(token_data)
            service = build('blogger', 'v3', credentials=creds)
        except Exception as e:
            print(f"❌ HATA: BLOGGER_TOKEN JSON formatı bozuk veya geçersiz! Detay: {e}")
            return

        blog_id = os.getenv('BLOGGER_ID')
        
        # 2. Zaman Ayarları
        istanbul_tz = pytz.timezone('Europe/Istanbul')
        simdi = datetime.now(istanbul_tz)
        aylar = {1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
                 7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"}
        
        gercek_baslik = f"{simdi.strftime('%d')} {aylar[simdi.month]} {simdi.strftime('%Y')} Altın Fiyatları"
        saat_str, saat_id = simdi.strftime("%H:%M"), simdi.strftime("%H%M")

        # 3. Veri Çekme ve Hata Ayıklama
        url = "https://ayarlar.bingolder.com/"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ HATA: Fiyat sitesine ulaşılamıyor (Kod: {response.status_code})")
            return

        try:
            data = response.json()
        except:
            print("❌ HATA: Siteden dönen veri JSON formatında değil!")
            print(f"Gelen ham veri: {response.text[:100]}")
            return

        rows = data.get('values', [])
        if not rows:
            print("⚠️ Veri listesi boş.")
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

        if 'kur' not in fiyatlar:
            print("❌ HATA: Veriler arasında 'kur' bilgisi bulunamadı.")
            return

        kur_alis = fiyatlar['kur']['alis']
        kur_satis = fiyatlar['kur']['satis']

        # 4. Ürün Listesi
        isimlendirme = [
            ("kur", "KUR"), ("has", "Çekme Altın (0,995)"), ("tel", "Burma Bilezik"),
            ("iscilikli", "İşçilikli Ürün"), ("ondort", "14 Ayar Altın"), 
            ("besli", "Beşli Ata"), ("ata", "Ata Lira"), ("ziynet", "Ziynet Altın"),
            ("yarım", "Yarım Altın"), ("ceyrek", "Çeyrek Altın"),
            ("gram²⁴", "Gram Altın (0,995)"), ("ons", "ONS (USD)")
        ]

        # 5. HTML Tablo Oluşturma
        yeni_tablo_html = f"""<div id="tab-{saat_id}" class="altin-tab-icerik" style="display:none;">
            <table style="width:100%; border-collapse: collapse; border: 1px solid #D4AF37; font-family: Arial;">
                <thead><tr style="background-color: #D4AF37; color: white;"><th style="padding:10px;">Ürün</th><th style="padding:10px;">Alış</th><th style="padding:10px;">Satış</th></tr></thead>
                <tbody>"""
        
        for anahtar, gorunur_ad in isimlendirme:
            if anahtar in fiyatlar:
                deger = fiyatlar[anahtar]
                f_alis = int(deger['alis']) if anahtar in ["kur", "ons"] else yuvarla(kur_alis * deger['alis'])
                f_satis = int(deger['satis']) if anahtar in ["kur", "ons"] else yuvarla(kur_satis * deger['satis'])
                yeni_tablo_html += f"<tr><td style='padding:8px; border-bottom:1px solid #eee;'><b>{gorunur_ad}</b></td><td>{f_alis:,}</td><td style='color:#b8860b; font-weight:bold;'>{f_satis:,}</td></tr>"
        
        yeni_tablo_html += "</tbody></table></div>"

        # 6. Blogger İşlemleri
        query = f'title:"{gercek_baslik}"'
        search_results = service.posts().search(blogId=blog_id, q=query).execute()
        existing_post = next((item for item in search_results.get('items', []) if item['title'] == gercek_baslik), None)

        arsiv_notu = '<p id="arsiv-notu" style="margin-top:15px; padding:10px; background:#f9f9f9; border-left:4px solid #D4AF37; font-size:14px; font-family:Arial, sans-serif; color:#555;">⚠️ Veriler arşiv niteliğindedir.</p>'

        if existing_post:
            content = existing_post['content']
            yeni_option = f'<option value="tab-{saat_id}">{saat_str}</option>'
            content = content.replace('</select>', yeni_option + '</select>')
            updated_content = content.replace('<p id="arsiv-notu"', yeni_tablo_html + '<p id="arsiv-notu"') if 'id="arsiv-notu"' in content else content + yeni_tablo_html
            service.posts().update(blogId=blog_id, postId=existing_post['id'], body={'title': gercek_baslik, 'content': updated_content, 'labels': ['Altın Fiyatları']}).execute()
            print(f"✅ Blogger Güncellendi: {saat_str}")
        else:
            js_stil = "<script>function tabloDegistir(sel) { var x = document.getElementsByClassName('altin-tab-icerik'); for (var i = 0; i < x.length; i++) { x[i].style.display = 'none'; } document.getElementById(sel.value).style.display = 'block'; } window.onload = function() { var s = document.getElementById('saat-select'); if(s) { s.selectedIndex = s.options.length - 1; tabloDegistir(s); } };</script>"
            ana_icerik = js_stil + f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding: 12px 15px; background: #f4f4f4; border: 1px solid #D4AF37; gap: 10px;"><label>🕒 Saat Seçin:</label><select id="saat-select" onchange="tabloDegistir(this)"><option value="tab-{saat_id}">{saat_str}</option></select></div>'
            ana_icerik += yeni_tablo_html.replace('display:none;', 'display:block;') + arsiv_notu
            gecici = service.posts().insert(blogId=blog_id, body={'title': simdi.strftime("%d-%m-%Y"), 'content': ana_icerik, 'labels': ['Altın Fiyatları']}).execute()
            service.posts().update(blogId=blog_id, postId=gecici['id'], body={'title': gercek_baslik, 'content': ana_icerik, 'labels': ['Altın Fiyatları']}).execute()
            print(f"🌟 Yeni Blogger Yazısı: {gercek_baslik}")

        # 7. Instagram
        insta_mesaj = instagram_metni_olustur(fiyatlar, isimlendirme, gercek_baslik, kur_alis, kur_satis)
        instagram_paylas(insta_mesaj)

    except Exception as e:
        print(f"❌ KRİTİK SİSTEM HATASI: {str(e)}")

if __name__ == "__main__":
    run_bot()
