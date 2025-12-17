# 🚀 EdafDesk Installer Build Rehberi

## Windows Installer Oluşturma

### Gereksinimler:
1. **Inno Setup** indirin: https://jrsoftware.org/isdl.php
2. Kurulumu tamamlayın

### Adımlar:

1. **EXE'yi build edin:**
```bash
python -m PyInstaller --onefile --windowed --name=EdafDesk --noconsole main.py
```

2. **İnstaller'ı derleyin:**
- `installer.iss` dosyasına sağ tıklayın
- **"Compile"** seçin
- Veya komut satırından:
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

3. **Sonuç:**
- `installer_output` klasöründe `EdafDesk_Setup_1.0.0.exe` dosyası oluşur
- Bu dosya tam bir Windows installer'dır!

---

## Mac DMG Oluşturma

GitHub Actions otomatik olarak Mac DMG oluşturuyor.

### Manuel Build (Mac'te):
```bash
# Python bağımlılıkları
pip3 install Pillow pynput pyinstaller

# App oluştur
pyinstaller --onefile --windowed --name=EdafDesk --noconsole main.py

# DMG oluştur
mkdir -p dmg_temp
cp -r dist/EdafDesk.app dmg_temp/
hdiutil create -volname "EdafDesk" -srcfolder dmg_temp -ov -format UDZO EdafDesk.dmg
```

---

## GitHub Actions ile Otomatik Build

Her push sonrası otomatik olarak oluşturulur:
- ✅ Windows EXE
- ✅ Windows Setup.exe (Installer)
- ✅ Mac DMG
- ✅ Mac .app

**İndirme:** https://github.com/emirozcopuredaftech/EdafDesk/actions
