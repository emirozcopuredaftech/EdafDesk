# EdafDesk Relay Server Kurulum Rehberi

## Relay Server Nedir?

Relay sunucu, host ve client'ların internet üzerinden birbirine bağlanmasını sağlar. Anydesk gibi çalışır - merkezi bir sunucu üzerinden tüm bağlantılar geçer.

## Kurulum

### 1. VPS/Sunucu Gereksinimi

Relay server için bir VPS'e ihtiyacınız var. Öneriler:
- **DigitalOcean** - 6$/ay (1GB RAM, 1 vCPU)
- **Linode** - 5$/ay  
- **AWS EC2** - Free tier (1 yıl)
- **Hetzner** - 4€/ay

### 2. Sunucuya Python Kurulumu

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip -y

# CentOS/RHEL
sudo yum install python3 python3-pip -y
```

### 3. Relay Server Dosyasını Yükle

```bash
# Sunucuya bağlan
ssh root@SUNUCU_IP

# EdafDesk dizini oluştur
mkdir edafdesk
cd edafdesk

# relay_server.py dosyasını yükle (scp veya git ile)
```

**relay_server.py** dosyasını sunucuya kopyalayın.

### 4. Servisi Başlat

#### Manuel Başlatma:
```bash
python3 relay_server.py
```

#### Systemd ile Otomatik Başlatma (Önerilen):

```bash
# Servis dosyası oluştur
sudo nano /etc/systemd/system/edafdesk-relay.service
```

İçeriği:
```ini
[Unit]
Description=EdafDesk Relay Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/edafdesk
ExecStart=/usr/bin/python3 /root/edafdesk/relay_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Servisi aktif et:
```bash
sudo systemctl daemon-reload
sudo systemctl enable edafdesk-relay
sudo systemctl start edafdesk-relay

# Durumu kontrol et
sudo systemctl status edafdesk-relay
```

### 5. Firewall Ayarları

#### Ubuntu UFW:
```bash
sudo ufw allow 9999/tcp
sudo ufw enable
sudo ufw status verbose
```

#### **ORACLE CLOUD ÖNEMLİ!**

Oracle Cloud kullanıyorsanız **IKI YER**de ayar yapmalısınız:

**A) Ubuntu UFW (Yukarıda yaptık ✅)**

**B) Oracle Cloud Security List (KRİTİK!):**

1. **Oracle Cloud Console** → https://cloud.oracle.com
2. Menü (☰) → **Networking** → **Virtual Cloud Networks**
3. VCN'inizi seçin (test-vcn gibi)
4. Sol menü → **Security Lists**
5. **Default Security List for [VCN-name]** tıklayın
6. **Ingress Rules** sekmesi
7. **Add Ingress Rules** butonu

**Kural Ayarları:**
```
Stateless: ❌ (boş bırak)
Source Type: CIDR
Source CIDR: 0.0.0.0/0
IP Protocol: TCP
Source Port Range: (boş - All)
Destination Port Range: 9999
Description: EdafDesk Relay Server
```

8. **Add Ingress Rules** → Kaydet

**⚠️ Bu adım olmadan dışarıdan bağlantı ASLA gelmez!**

#### Test:
```bash
# Sunucuda port dinliyor mu?
ss -tuln | grep 9999

# Dışarıdan test (başka bilgisayardan)
# Windows PowerShell:
Test-NetConnection -ComputerName SUNUCU_IP -Port 9999

# Linux/Mac:
nc -zv SUNUCU_IP 9999
```

#### Diğer Cloud Sağlayıcılar:

**AWS EC2:**
- Security Groups → Inbound Rules → Add Rule
- Type: Custom TCP, Port: 9999, Source: 0.0.0.0/0

**DigitalOcean:**
- Networking → Firewalls → Add Rule
- Type: TCP, Port: 9999, Sources: All IPv4

**Firewalld (CentOS):**
```bash
sudo firewall-cmd --permanent --add-port=9999/tcp
sudo firewall-cmd --reload
```

### 6. Client Tarafında Ayar

EdafDesk uygulamasında:
1. "Bağlantı Modu" → **İnternet**
2. "Relay Sunucu" → Sunucunuzun IP'sini girin (örn: `123.45.67.89`)
3. Host olarak başlatın ve ID'nizi alın
4. Client tarafta bu ID ile bağlanın

## Test

### Sunucu Testi:
```bash
# Log izle
sudo journalctl -u edafdesk-relay -f

# Port dinleme kontrolü
ss -tuln | grep 9999
```

### Client Testi:
```bash
# Telnet ile bağlantı test
telnet SUNUCU_IP 9999
```

## Güvenlik

### SSL/TLS Ekleme (İsteğe Bağlı)

Relay server'a SSL eklemek için:

```python
import ssl

# relay_server.py içinde
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('cert.pem', 'key.pem')
self.server_socket = context.wrap_socket(self.server_socket, server_side=True)
```

### Temel Güvenlik Önerileri:

1. **Firewall:** Sadece 9999 portunu açık tutun
2. **Fail2Ban:** Brute force saldırılarına karşı
3. **Rate Limiting:** Aşırı bağlantıyı engelleyin
4. **Monitoring:** Sunucu kaynaklarını izleyin

## Sorun Giderme

### Bağlantı Kurulamıyor

```bash
# Port dinliyor mu?
ss -tuln | grep 9999

# Servis çalışıyor mu?
sudo systemctl status edafdesk-relay

# Firewall açık mı?
sudo ufw status
```

### Yüksek CPU/RAM Kullanımı

```bash
# Performans izleme
htop

# Bağlantı sayısı
ss -t | grep 9999 | wc -l
```

## Maliyet Optimizasyonu

- **Free Tier:** AWS EC2, Google Cloud (1 yıl ücretsiz)
- **Oracle Cloud:** Always free 2 VM
- **Heroku:** Free dyno (yeterli performans olmayabilir)

## Destek

Sorun yaşarsanız:
1. Logları kontrol edin: `sudo journalctl -u edafdesk-relay -n 100`
2. GitHub Issues'da bildirin
3. Discord kanalımıza katılın
