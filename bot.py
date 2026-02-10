def upload_to_instagram(img_path):
    SESSION_ID = os.getenv('INSTA_SESSIONID')
    
    if not SESSION_ID:
        print("HATA: INSTA_SESSIONID Secrets ayarı yapılmamış!")
        return

    cl = Client()
    
    # KRİTİK AYAR: Botu Chrome tarayıcısı gibi tanıtıyoruz
    cl.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

    try:
        print("Session ID ile giriş yapılıyor...")
        
        # Giriş yapmadan önce cookieleri manuel ayarla (Hata ihtimalini düşürür)
        cl.set_settings({"cookies": {"sessionid": SESSION_ID}})
        
        # Şifresiz giriş
        cl.login_by_sessionid(SESSION_ID)
        
        # Giriş başarılı mı kontrol et
        user_info = cl.account_info().dict()
        print(f"Giriş Başarılı: {user_info['username']}")
        
        caption = "Bingöl Güncel Altın Fiyatları 📊 #bingol #altin #kuyumcu"
        cl.photo_upload(img_path, caption)
        print("Paylaşım başarıyla yapıldı!")
        
    except Exception as e:
        print(f"Instagram hatası: {e}")
        print("Tavsiye: Tarayıcıdan yeni bir sessionid alıp Secret'ı güncellemeyi deneyin.")
