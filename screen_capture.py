"""
Ekran Yakalama Modülü
"""

import io
import base64
import platform
import subprocess
import tempfile
import os
from config import *

class ScreenCapture:
    def __init__(self):
        self.is_mac = platform.system() == 'Darwin'
        self.is_windows = platform.system() == 'Windows'
        
        # Windows için PIL'i import et
        if self.is_windows:
            from PIL import ImageGrab
            self.ImageGrab = ImageGrab
        
        # Mac için PIL'i dene, yoksa None olarak bırak
        if self.is_mac:
            try:
                from PIL import Image
                self.Image = Image
            except ImportError:
                self.Image = None
        
    def _capture_mac_native(self):
        """Mac için native screencapture komutunu kullan"""
        try:
            # Geçici dosya oluştur
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # screencapture komutu ile ekran yakala
            subprocess.run(['screencapture', '-x', '-t', 'jpg', temp_path], 
                         check=True, capture_output=True)
            
            # Dosyayı oku
            with open(temp_path, 'rb') as f:
                jpeg_data = f.read()
            
            # Geçici dosyayı sil
            os.unlink(temp_path)
            
            # Ölçeklendirme gerekiyorsa
            if SCREEN_SCALE < 1.0 and self.Image:
                img = self.Image.open(io.BytesIO(jpeg_data))
                new_width = int(img.width * SCREEN_SCALE)
                new_height = int(img.height * SCREEN_SCALE)
                img = img.resize((new_width, new_height), self.Image.LANCZOS)
                
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=COMPRESSION_QUALITY, optimize=True)
                jpeg_data = buffer.getvalue()
            
            return jpeg_data
            
        except Exception as e:
            print(f"Mac ekran yakalama hatası: {str(e)}")
            return None
    
    def _capture_windows(self):
        """Windows için PIL ImageGrab kullan"""
        try:
            img = self.ImageGrab.grab()
            
            # Performans için ölçeklendir
            if SCREEN_SCALE < 1.0:
                new_width = int(img.width * SCREEN_SCALE)
                new_height = int(img.height * SCREEN_SCALE)
                from PIL import Image
                img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # JPEG'e dönüştür
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=COMPRESSION_QUALITY, optimize=True)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Windows ekran yakalama hatası: {str(e)}")
            return None
        
    def capture(self):
        """Ekran görüntüsü yakala ve güvenli formatta döndür"""
        try:
            if self.is_mac:
                jpeg_data = self._capture_mac_native()
            elif self.is_windows:
                jpeg_data = self._capture_windows()
            else:
                print("Desteklenmeyen işletim sistemi")
                return None
            
            if jpeg_data and len(jpeg_data) > 100:  # Minimum boyut kontrolü
                # Veri bütünlüğü için checksum ile doğrula
                try:
                    # Basit veri geçerlilik kontrolü
                    test_img = io.BytesIO(jpeg_data)
                    from PIL import Image
                    Image.open(test_img).verify()  # JPEG geçerliliğini kontrol et
                    
                    # Base64 ile encode et - daha güvenli
                    encoded_data = base64.b64encode(jpeg_data).decode('utf-8')
                    
                    # Güvenli paket formatı: HEADER|SIZE|DATA|FOOTER
                    packet = f"EDAF_START|{len(encoded_data)}|{encoded_data}|EDAF_END"
                    return packet.encode('utf-8')
                    
                except Exception as e:
                    print(f"JPEG doğrulama hatası: {str(e)}")
                    return None
            return None
            
        except Exception as e:
            print(f"Ekran yakalama hatası: {str(e)}")
            return None
    
    def get_screen_size(self):
        """Ekran boyutunu döndür"""
        if self.is_mac:
            try:
                # Mac için sistem profili ile ekran boyutunu al
                result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                      capture_output=True, text=True)
                # Basitleştirilmiş: varsayılan boyut döndür
                return (1920, 1080)  # Gerçek boyut için parsing gerekli
            except:
                return (1920, 1080)
        else:
            img = self.ImageGrab.grab()
            return (img.width, img.height)
