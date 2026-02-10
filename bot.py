def upload_to_instagram(img_path):
    SESSION_ID = os.getenv('INSTA_SESSIONID')
    
    if not SESSION_ID:
        print("HATA: INSTA_SESSIONID Secrets ayarı yapılmamış!")
        return

    cl = Client()
    
    # 1. Tarayıcı (User-Agent) bilgilerini Chrome olarak ayarla
    cl.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:
        print("Session ID ile giriş deneniyor...")
        
        # 2. SessionID'yi doğrudan çerez olarak ekle (data hatasını önlemek için)
        cl.set_settings({
            "cookies": [
                {
                    "name": "sessionid",
                    "value": SESSION_ID,
                    "domain": ".instagram.com",
                    "path": "/",
                }
            ]
        })
        
        # 3. Giriş yap
        cl.login_by_sessionid(SESSION_ID)
        
        # 4. Girişi doğrula
        me = cl.account_info().dict()
        print(f"Giriş Başarılı: {me['username']}")
        
        # 5. Paylaşım
        caption = "Bingöl Güncel Altın Fiyatları 📊\n\n#bingol #altin #kuyumcu #bingolder"
        cl.photo_upload(img_path, caption)
        print("Paylaşım başarıyla yapıldı!")
        
    except Exception as e:
        print(f"Instagram hatası: {e}")
        print("İPUCU: Hata 'data' ise yeni bir sessionid alıp Secret'ı güncelleyin.")
