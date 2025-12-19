"""
Relay Client - İnternet üzerinden bağlanan taraf
"""

import socket
import threading
import base64
import struct
import tkinter as tk
from PIL import Image, ImageTk
import io
from config import *

class RelayClient:
    def __init__(self, host_id, relay_server=RELAY_SERVER, relay_port=RELAY_PORT, log_callback=None):
        self.host_id = host_id
        self.relay_server = relay_server
        self.relay_port = relay_port
        self.log = log_callback or print
        self.running = False
        self.socket = None
        self.screen_window = None
        
    def connect(self):
        """Relay üzerinden host'a bağlan"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.relay_server, self.relay_port))
            
            # CLIENT olduğunu ve host ID'yi bildir
            self.socket.send(f"CLIENT:{self.host_id}".encode())
            
            # Yanıt bekle
            response = self.socket.recv(1024).decode()
            
            if response.startswith("OK:"):
                self.log(f"✅ Host {self.host_id} ile bağlantı kuruldu!")
                self.running = True
                
                # Ekran penceresini aç
                self.create_screen_window()
                return True
                
            elif response.startswith("ERROR:"):
                error = response.split(":")[1]
                if error == "HOST_NOT_FOUND":
                    self.log(f"❌ Host bulunamadı! ID: {self.host_id}")
                else:
                    self.log(f"❌ Bağlantı hatası: {error}")
                return False
                
        except Exception as e:
            self.log(f"❌ Relay'e bağlanılamadı: {str(e)}")
            return False
    
    def create_screen_window(self):
        """Ekran görüntüleme penceresi oluştur"""
        self.screen_window = tk.Toplevel()
        self.screen_window.title(f"EdafDesk - Host {self.host_id}")
        self.screen_window.geometry("1280x720")
        self.screen_window.configure(bg='black')
        
        self.canvas = tk.Canvas(self.screen_window, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Mouse ve keyboard event'leri
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.canvas.bind('<Button-1>', lambda e: self.on_mouse_click(1, True))
        self.canvas.bind('<ButtonRelease-1>', lambda e: self.on_mouse_click(1, False))
        self.canvas.bind('<Button-3>', lambda e: self.on_mouse_click(2, True))
        self.canvas.bind('<ButtonRelease-3>', lambda e: self.on_mouse_click(2, False))
        self.canvas.bind('<MouseWheel>', self.on_mouse_scroll)
        self.screen_window.bind('<KeyPress>', lambda e: self.on_key_press(e, True))
        self.screen_window.bind('<KeyRelease>', lambda e: self.on_key_press(e, False))
        
        self.canvas.focus_set()
        
        # Pencere kapatma
        self.screen_window.protocol("WM_DELETE_WINDOW", self.disconnect)
        
        # Ekran alma thread'i
        receive_thread = threading.Thread(target=self.receive_screen, daemon=True)
        receive_thread.start()
    
    def receive_screen(self):
        """Ekran görüntülerini al"""
        while self.running:
            try:
                # Veri boyutunu al
                data_size_bytes = self.socket.recv(4)
                if not data_size_bytes:
                    break
                
                data_size = struct.unpack('!I', data_size_bytes)[0]
                
                # Veriyi al
                data = b''
                while len(data) < data_size:
                    packet = self.socket.recv(min(65536, data_size - len(data)))
                    if not packet:
                        break
                    data += packet
                
                # Güvenli paket parse et
                try:
                    try:
                        packet_str = data.decode('utf-8', errors='ignore')
                    except UnicodeDecodeError:
                        # Eğer UTF-8 değilse, latin-1 dene
                        packet_str = data.decode('latin-1', errors='ignore')
                    
                    # EDAF paket formatını kontrol et - daha esnek kontrol
                    if 'EDAF_START|' not in packet_str or '|EDAF_END' not in packet_str:
                        # Debug bilgisi
                        if len(packet_str) > 0:
                            self.log(f"⚠️ Paket format hatası. İlk 50 karakter: {packet_str[:50]}")
                        continue
                    
                    # Paket bileşenlerini ayır
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
                    
                    encoded_data = parts[2]
                    
                    # Base64 decode et
                    jpeg_data = base64.b64decode(encoded_data.encode('utf-8'))
                    
                except (ValueError, IndexError, base64.binascii.Error) as e:
                    self.log(f"⚠️ Paket parse hatası: {str(e)[:50]}...")
                    continue
                
                # Görüntüle
                self.display_screen(jpeg_data)
                
            except Exception as e:
                if self.running:
                    self.log(f"❌ Ekran alma hatası: {str(e)}")
                break
        
        self.disconnect()
    
    def display_screen(self, jpeg_data):
        """Ekranı göster"""
        try:
            img = Image.open(io.BytesIO(jpeg_data))
            
            # Canvas boyutuna sığdır
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                img = img.resize((canvas_width, canvas_height), Image.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            
            # Flicker'ı önlemek için tek seferde güncelle
            def update_canvas():
                try:
                    if not hasattr(self, 'image_id') or not self.canvas.find_all():
                        self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                    else:
                        self.canvas.itemconfig(self.image_id, image=photo)
                    
                    # Reference'ı sakla (garbage collection için)
                    self.current_photo = photo
                    
                except Exception as e:
                    print(f"Canvas güncelleme hatası: {str(e)}")
            
            # Ana thread'de çalıştır
            if hasattr(self, 'screen_window') and self.screen_window:
                self.screen_window.after(0, update_canvas)
            
        except Exception as e:
            print(f"Görüntü gösterme hatası: {str(e)}")
    
    def on_mouse_move(self, event):
        """Mouse hareketi"""
        if not self.running:
            return
        
        try:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            x_ratio = event.x / canvas_width
            y_ratio = event.y / canvas_height
            
            command = {
                'type': 'mouse_move',
                'x': x_ratio,
                'y': y_ratio
            }
            
            self.send_input(command)
        except:
            pass
    
    def on_mouse_click(self, button, pressed):
        """Mouse tıklama"""
        command = {
            'type': 'mouse_click',
            'button': button,
            'pressed': pressed
        }
        self.send_input(command)
    
    def on_mouse_scroll(self, event):
        """Mouse scroll"""
        command = {
            'type': 'mouse_scroll',
            'dx': 0,
            'dy': event.delta // 120
        }
        self.send_input(command)
    
    def on_key_press(self, event, pressed):
        """Klavye basma"""
        command = {
            'type': 'key_press',
            'key': event.keysym,
            'pressed': pressed
        }
        self.send_input(command)
    
    def send_input(self, command):
        """Input komutunu gönder"""
        try:
            import json
            # JSON kullan - daha güvenli
            json_str = json.dumps(command)
            # Komut paket formatı
            packet = f"CMD_START|{len(json_str)}|{json_str}|CMD_END"
            data = packet.encode('utf-8')
            self.socket.send(data)
        except Exception as e:
            if self.running:
                self.log(f"⚠️ Input gönderme hatası: {str(e)}")
    
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
        
        self.log("🔴 Bağlantı kesildi")
