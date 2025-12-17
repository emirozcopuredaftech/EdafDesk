"""
Ekran Yakalama Modülü
"""

import io
from PIL import ImageGrab
import pickle
from config import *

class ScreenCapture:
    def __init__(self):
        pass
        
    def capture(self):
        """Ekran görüntüsü yakala ve JPEG formatında döndür"""
        try:
            # PIL ImageGrab kullan (threading sorunsuz)
            img = ImageGrab.grab()
            
            # Performans için ölçeklendir
            if SCREEN_SCALE < 1.0:
                new_width = int(img.width * SCREEN_SCALE)
                new_height = int(img.height * SCREEN_SCALE)
                from PIL import Image
                img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # JPEG'e dönüştür (sıkıştırma için)
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=COMPRESSION_QUALITY, optimize=True)
            jpeg_data = buffer.getvalue()
            
            # Pickle ile serialize et
            return pickle.dumps(jpeg_data)
            
        except Exception as e:
            print(f"Ekran yakalama hatası: {str(e)}")
            return None
    
    def get_screen_size(self):
        """Ekran boyutunu döndür"""
        img = ImageGrab.grab()
        return (img.width, img.height)
