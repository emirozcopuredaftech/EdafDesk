"""
Yapılandırma Ayarları
"""

# Network Ayarları
DEFAULT_PORT = 5555
BUFFER_SIZE = 65536
COMPRESSION_QUALITY = 60  # JPEG kalitesi (0-100)
FPS = 15  # Saniyede kare sayısı (daha smooth)

# Relay Sunucu Ayarları
RELAY_SERVER = "localhost"  # Varsayılan relay sunucu adresi (değiştirilebilir)
RELAY_PORT = 9999

# Güvenlik
MAX_CONNECTIONS = 5
CONNECTION_TIMEOUT = 300  # saniye

# Ekran Ayarları
SCREEN_SCALE = 0.7  # Ekran ölçeklendirme (performans için)

# Renkler
PRIMARY_COLOR = "#2196F3"
SUCCESS_COLOR = "#4CAF50"
ERROR_COLOR = "#F44336"
BG_COLOR = "#FFFFFF"
