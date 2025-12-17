# EdafDesk - Uzak Masaüstü Uygulaması

Python ile geliştirilmiş profesyonel uzak masaüstü kontrol uygulaması.

**Geliştirici:** Edaf

## 🚀 Özellikler

- ✅ Ekran paylaşımı (Host modü)
- ✅ Uzaktan bağlanma (Client modü)
- ✅ Mouse ve klavye kontrolü
- ✅ Gerçek zamanlı ekran aktarımı
- ✅ Sıkıştırılmış veri transferi
- ✅ Kullanıcı dostu arayüz

## 📋 Gereksinimler

- Python 3.8 veya üzeri
- Windows işletim sistemi (şu an için)

## 🔧 Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Uygulamayı başlatın:
```bash
python main.py
```

## 📖 Kullanım

### Host Modu (Ekranı Paylaşan)

1. "Ekranımı Paylaş (Host)" bölümünde IP adresinizi görün
2. Port numarasını kontrol edin (varsayılan: 5555)
3. "▶ Ekran Paylaşımını Başlat" butonuna tıklayın
4. IP adresinizi bağlanacak kişiye verin

### Client Modu (Bağlanan)

1. "Uzak Bilgisayara Bağlan (Client)" bölümüne host'un IP adresini girin
2. Port numarasını girin
3. "🔗 Bağlan" butonuna tıklayın
4. Uzak ekran penceresi açılacaktır

## 🎮 Kontroller

- **Mouse**: Uzak bilgisayarın mouse'unu kontrol eder
- **Klavye**: Uzak bilgisayara klavye girişi gönderir
- **Sol Tık**: Uzak bilgisayarda sol tıklama
- **Sağ Tık**: Uzak bilgisayarda sağ tıklama

## ⚙️ Yapılandırma

`config.py` dosyasından ayarları değiştirebilirsiniz:

- `DEFAULT_PORT`: Varsayılan port numarası
- `FPS`: Saniyedeki kare sayısı (performans)
- `COMPRESSION_QUALITY`: JPEG kalitesi (0-100)
- `SCREEN_SCALE`: Ekran ölçeklendirme (performans)

## 🔒 Güvenlik Notları

⚠️ **Önemli**: Bu uygulama temel bir prototiptir ve şifreleme içermez. Güvenli ağlarda kullanın.

Güvenlik iyileştirmeleri için:
- SSL/TLS şifreleme ekleyin
- Kimlik doğrulama sistemi ekleyin
- Şifre koruması ekleyin

## 🛠️ Geliştirme Notları

### Proje Yapısı

```
PyRemoteControl/
├── main.py              # Ana başlatıcı
├── gui.py               # GUI arayüzü
├── host.py              # Host sunucu modülü
├── client.py            # Client bağlantı modülü
├── screen_capture.py    # Ekran yakalama
├── input_control.py     # Klavye/fare kontrolü
├── config.py            # Yapılandırma
└── requirements.txt     # Bağımlılıklar
```

### Performans İyileştirmeleri

- JPEG sıkıştırma kullanılır (COMPRESSION_QUALITY)
- Ekran ölçeklendirme (SCREEN_SCALE)
- Veri sıkıştırma (zlib)
- FPS sınırlama

## 📝 Lisans

Bu proje eğitim amaçlıdır. Ticari kullanım için uygun değildir.

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Pull request göndermekten çekinmeyin.

## 📧 İletişim

Sorularınız için issue açabilirsiniz.

---

**Geliştirici**: Edaf
**Proje**: EdafDesk
**Versiyon**: 1.0.0

🚀 **Made with ❤️ by Edaf**
