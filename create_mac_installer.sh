#!/bin/bash
# Mac Installer Oluşturma Script'i

APP_NAME="EdafDesk"
APP_DIR="dist/${APP_NAME}.app"
PKG_NAME="${APP_NAME}_Installer.pkg"
IDENTIFIER="com.edaf.edafdesk"

echo "🍎 Mac Installer oluşturuluyor..."

# .app dosyasının varlığını kontrol et
if [ ! -d "$APP_DIR" ]; then
    echo "❌ Hata: $APP_DIR bulunamadı!"
    exit 1
fi

# Geçici dizin oluştur
TEMP_DIR="temp_installer"
mkdir -p "$TEMP_DIR/Applications"

# .app'i kopyala
cp -R "$APP_DIR" "$TEMP_DIR/Applications/"

# PKG oluştur
echo "📦 .pkg dosyası oluşturuluyor..."
pkgbuild --root "$TEMP_DIR" \
         --identifier "$IDENTIFIER" \
         --version "1.0.0" \
         --install-location "/" \
         "$PKG_NAME"

# Temizlik
rm -rf "$TEMP_DIR"

echo "✅ Installer hazır: $PKG_NAME"
ls -lh "$PKG_NAME"
