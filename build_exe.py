"""
EdafDesk EXE Build Script
PyInstaller kullanarak tek dosya EXE oluşturur
"""

import os
import subprocess
import sys

def build_exe():
    print("🚀 EdafDesk EXE Build Başlatılıyor...")
    print("=" * 50)
    
    # PyInstaller komutu
    command = [
        'pyinstaller',
        '--onefile',  # Tek dosya
        '--windowed',  # Console penceresi yok
        '--name=EdafDesk',  # EXE adı
        '--icon=NONE',  # İkon (varsa eklenebilir)
        '--add-data=config.py;.',  # Config dosyasını ekle
        '--hidden-import=PIL._tkinter_finder',  # Gizli importlar
        '--hidden-import=pynput.keyboard._win32',
        '--hidden-import=pynput.mouse._win32',
        '--noconsole',  # Console gizle
        'main.py'
    ]
    
    print(f"📦 Komut: {' '.join(command)}")
    print("=" * 50)
    
    try:
        # Build işlemini başlat
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        
        print("=" * 50)
        print("✅ Build başarılı!")
        print("📁 EXE dosyası: dist/EdafDesk.exe")
        print("=" * 50)
        
    except subprocess.CalledProcessError as e:
        print("❌ Build hatası!")
        print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("❌ PyInstaller bulunamadı!")
        print("Lütfen şu komutu çalıştırın: pip install pyinstaller")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
