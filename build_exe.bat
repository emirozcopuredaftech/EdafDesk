@echo off
echo ========================================
echo EdafDesk EXE Builder
echo by Edaf
echo ========================================
echo.

echo [1/3] PyInstaller yukleniyor...
pip install pyinstaller

echo.
echo [2/3] EXE olusturuluyor...
pyinstaller --onefile --windowed --name=EdafDesk --noconsole main.py

echo.
echo [3/3] Temizlik yapiliyor...
rmdir /s /q build
del /q EdafDesk.spec

echo.
echo ========================================
echo TAMAMLANDI!
echo EXE Dosyasi: dist\EdafDesk.exe
echo ========================================
pause
