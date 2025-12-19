"""
Client Modülü - Uzaktan Bağlanan Taraf
"""

import socket
import threading
import base64
import zlib
import tkinter as tk
from PIL import Image, ImageTk
import io
from config import *

class ClientConnection:
    def __init__(self, host_ip, host_port, log_callback=None):
        self.host_ip = host_ip
        self.host_port = host_port
        self.log = log_callback or print
        self.running = False
        self.socket = None
        self.screen_window = None
        
    def connect(self):
        """Host'a bağlan"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host_ip, self.host_port))
            
            self.log(f"⏳ Bağlantı kuruluyor, onay bekleniyor...")
            
            # Host'tan onay bekle
            approval_response = self.socket.recv(1024)
            
            if approval_response == b"REJECTED":
                self.log(f"❌ Bağlantı reddedildi!")
                self.socket.close()
                self.running = False
                return False
            elif approval_response == b"APPROVED":
                self.log(f"✅ Bağlantı onaylandı!")
                self.running = True
            else:
                self.log(f"⚠️ Bilinmeyen yanıt")
                self.running = True
            
            self.log(f"✅ {self.host_ip}:{self.host_port} adresine bağlanıldı!")
            
            # Ekran görüntüleme penceresini aç
            self.create_screen_window()
            
            # Ekran alma thread'i
            receive_thread = threading.Thread(target=self.receive_screen, daemon=True)
            receive_thread.start()
            
            return True
            
        except Exception as e:
            self.log(f"❌ Bağlantı başarısız: {str(e)}")
            self.running = False
            return False
    
    def create_screen_window(self):
        """Uzak ekranı gösteren pencere oluştur"""
        self.screen_window = tk.Toplevel()
        self.screen_window.title(f"Uzak Ekran - {self.host_ip}")
        self.screen_window.geometry("1024x768")
        
        # Canvas (ekran görüntüsü için)
        self.canvas = tk.Canvas(self.screen_window, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Mouse olayları
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        
        # Klavye olayları
        self.screen_window.bind("<Key>", self.on_key_press)
        
        # Pencere kapanma
        self.screen_window.protocol("WM_DELETE_WINDOW", self.disconnect)
        
        self.log("🖥️ Uzak ekran penceresi açıldı")
    
    def receive_screen(self):
        """Ekran görüntüsünü sürekli al ve göster"""
        while self.running:
            try:
                # Veri boyutunu al (4 byte)
                size_data = self.recv_all(4)
                if not size_data:
                    break
                
                size = int.from_bytes(size_data, byteorder='big')
                
                # Sıkıştırılmış veriyi al
                compressed_data = self.recv_all(size)
                if not compressed_data:
                    break
                
                # Veriyi çöz
                try:
                    screen_data = zlib.decompress(compressed_data)
                    
                    # Güvenli paket formatını parse et
                    try:
                        packet_str = screen_data.decode('utf-8', errors='ignore')
                    except UnicodeDecodeError:
                        # Eğer UTF-8 değilse, latin-1 dene
                        packet_str = screen_data.decode('latin-1', errors='ignore')
                    
                    # EDAF paket formatını kontrol et - daha esnek kontrol
                    if 'EDAF_START|' not in packet_str or '|EDAF_END' not in packet_str:
                        # Debug bilgisi
                        if len(packet_str) > 0:
                            self.log(f"⚠️ Paket format hatası. İlk 50 karakter: {packet_str[:50]}")
                        continue
                    
                    # Paket bileşenlerini ayır
                    try:
                        # EDAF_START pozisyonunu bul
                        start_pos = packet_str.find('EDAF_START|')
                        end_pos = packet_str.find('|EDAF_END')
                        
                        if start_pos == -1 or end_pos == -1:
                            continue
                        
                        # Paket içeriğini çıkar
                        packet_content = packet_str[start_pos:end_pos + 9]  # +9 for |EDAF_END
                        parts = packet_content.split('|')
                        
                        if len(parts) != 4 or parts[0] != 'EDAF_START' or parts[3] != 'EDAF_END':
                            self.log(f"⚠️ Paket yapısı hatalı. Parts: {len(parts)}")
                            continue
                        
                        data_size = int(parts[1])
                        encoded_data = parts[2]
                        
                        # Base64 decode et
                        image_data = base64.b64decode(encoded_data.encode('utf-8'))
                        
                    except (ValueError, IndexError) as e:
                        self.log(f"⚠️ Paket parse hatası: {str(e)[:50]}...")
                        continue
                    
                    # PIL Image'e dönüştür
                    image = Image.open(io.BytesIO(image_data))
                    
                    # Canvas'a göster
                    self.display_image(image)
                    
                except (zlib.error, base64.binascii.Error) as e:
                    self.log(f"⚠️ Veri hatası, frame atlanıyor: {str(e)[:50]}...")
                    continue
                except Exception as e:
                    self.log(f"⚠️ Görüntü işleme hatası: {str(e)[:50]}...")
                    continue
                
            except Exception as e:
                if self.running:
                    self.log(f"⚠️ Ekran alma hatası: {str(e)}")
                break
        
        self.disconnect()
    
    def recv_all(self, size):
        """Belirtilen boyutta veri al"""
        if not self.socket:
            return None
            
        # Timeout ayarla
        self.socket.settimeout(10.0)
        data = b''
        try:
            while len(data) < size:
                remaining = size - len(data)
                packet = self.socket.recv(min(remaining, BUFFER_SIZE))
                if not packet:
                    return None
                data += packet
            return data
        except socket.timeout:
            self.log("⚠️ Veri alma zaman aşımı")
            return None
        except Exception as e:
            self.log(f"⚠️ Veri alma hatası: {str(e)}")
            return None
    
    def display_image(self, image):
        """Görüntüyü canvas'a göster"""
        if not self.screen_window or not self.canvas:
            return
        
        try:
            # Canvas boyutuna göre ölçeklendir
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                image = image.resize((canvas_width, canvas_height), Image.LANCZOS)
            
            # PhotoImage'e dönüştür
            photo = ImageTk.PhotoImage(image)
            
            # Canvas'ı güncelle (delete yerine itemconfig kullan - daha smooth)
            if not hasattr(self, 'image_id'):
                self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            else:
                self.canvas.itemconfig(self.image_id, image=photo)
            
            self.canvas.image = photo  # Referansı sakla
            self.canvas.update_idletasks()  # Smooth güncelleme
            
        except Exception as e:
            pass
    
    def on_mouse_move(self, event):
        """Mouse hareket olayı"""
        if not self.running:
            return
        
        try:
            # Canvas boyutunu al
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Oransal pozisyon hesapla
            rel_x = event.x / canvas_width
            rel_y = event.y / canvas_height
            
            # Komutu gönder
            command = {
                'type': 'mouse_move',
                'x': rel_x,
                'y': rel_y
            }
            self.send_command(command)
        except:
            pass
    
    def on_left_click(self, event):
        """Sol mouse tıklama olayı"""
        print(f"SOL TIK ALGILANDI! Running: {self.running}")
        if not self.running:
            return
        
        try:
            # Canvas boyutunu al
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Oransal pozisyon hesapla
            rel_x = event.x / canvas_width
            rel_y = event.y / canvas_height
            
            command = {
                'type': 'mouse_click',
                'button': 'left',
                'x': rel_x,
                'y': rel_y
            }
            self.send_command(command)
            print(f"✅ Sol tık komutu gönderildi (x={rel_x:.2f}, y={rel_y:.2f})")
            if self.log:
                self.log("🖱️ Sol tık gönderildi")
        except Exception as e:
            print(f"❌ Sol tık hatası: {str(e)}")
    
    def on_right_click(self, event):
        """Sağ mouse tıklama olayı"""
        print(f"SAĞ TIK ALGILANDI! Running: {self.running}")
        if not self.running:
            return
        
        try:
            # Canvas boyutunu al
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Oransal pozisyon hesapla
            rel_x = event.x / canvas_width
            rel_y = event.y / canvas_height
            
            command = {
                'type': 'mouse_click',
                'button': 'right',
                'x': rel_x,
                'y': rel_y
            }
            self.send_command(command)
            print(f"✅ Sağ tık komutu gönderildi (x={rel_x:.2f}, y={rel_y:.2f})")
            if self.log:
                self.log("🖱️ Sağ tık gönderildi")
        except Exception as e:
            print(f"❌ Sağ tık hatası: {str(e)}")
    
    def on_double_click(self, event):
        """Çift tıklama olayı"""
        print(f"ÇİFT TIK ALGILANDI! Running: {self.running}")
        if not self.running:
            return
        
        try:
            # Çift tık = iki kez sol tık
            for i in range(2):
                command = {
                    'type': 'mouse_click',
                    'button': 'left'
                }
                self.send_command(command)
            print("✅ Çift tık komutu gönderildi")
            if self.log:
                self.log("🖱️ Çift tık gönderildi")
        except Exception as e:
            print(f"❌ Çift tık hatası: {str(e)}")
    
    def on_key_press(self, event):
        """Klavye basma olayı"""
        if not self.running:
            return
        
        try:
            command = {
                'type': 'key_press',
                'key': event.char if event.char else event.keysym
            }
            self.send_command(command)
        except:
            pass
    
    def send_command(self, command):
        """Komut gönder"""
        try:
            import json
            # JSON kullan - daha güvenli
            json_str = json.dumps(command)
            # Komut paket formatı
            packet = f"CMD_START|{len(json_str)}|{json_str}|CMD_END"
            self.socket.sendall(packet.encode('utf-8'))
        except Exception as e:
            print(f"⚠️ Komut gönderme hatası: {str(e)}")
            pass
    
    def disconnect(self):
        """Bağlantıyı kes"""
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        if self.screen_window:
            try:
                self.screen_window.destroy()
            except:
                pass
        
        self.log("❌ Bağlantı kesildi")
