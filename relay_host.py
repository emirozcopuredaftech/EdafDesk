"""
Relay Host - İnternet üzerinden ekran paylaşan taraf
"""

import socket
import threading
import time
import json
import struct
from screen_capture import ScreenCapture
from input_control import InputController
from config import *

class RelayHost:
    def __init__(self, relay_server=RELAY_SERVER, relay_port=RELAY_PORT, log_callback=None):
        self.relay_server = relay_server
        self.relay_port = relay_port
        self.log = log_callback or print
        self.running = False
        self.socket = None
        self.host_id = None
        self.screen_capture = ScreenCapture()
        self.input_controller = InputController()
        
    def start(self):
        """Relay sunucuya bağlan ve ID al"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.relay_server, self.relay_port))
            
            # HOST olduğunu bildir
            self.socket.send(b"HOST")
            
            # ID al
            response = self.socket.recv(1024).decode()
            if response.startswith("ID:"):
                self.host_id = response.split(":")[1]
                self.log(f"✅ Relay'e bağlanıldı!")
                self.log(f"🎯 Sizin ID: {self.host_id}")
                self.running = True
                
                # Thread'leri başlat
                screen_thread = threading.Thread(target=self.send_screen, daemon=True)
                input_thread = threading.Thread(target=self.receive_input, daemon=True)
                
                screen_thread.start()
                input_thread.start()
                
                return True
            else:
                self.log(f"❌ ID alınamadı: {response}")
                return False
                
        except Exception as e:
            self.log(f"❌ Relay'e bağlanılamadı: {str(e)}")
            return False
    
    def send_screen(self):
        """Ekran görüntülerini gönder"""
        frame_delay = 1.0 / FPS
        
        while self.running:
            try:
                start_time = time.time()
                
                # Ekran yakala
                screen_data = self.screen_capture.capture()
                
                if screen_data:
                    # Boyutu gönder
                    data_size = len(screen_data)
                    self.socket.send(struct.pack('!I', data_size))
                    
                    # Veriyi gönder
                    self.socket.sendall(screen_data)
                
                # FPS kontrolü
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_delay - elapsed)
                time.sleep(sleep_time)
                
            except Exception as e:
                self.log(f"❌ Ekran gönderme hatası: {str(e)}")
                self.running = False
                break
    
    def receive_input(self):
        """Client'tan input komutlarını al"""
        buffer = b""  # Veri biriktirme buffer'ı
        while self.running:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                buffer += data
                
                # Komut paketlerini işle
                while b"CMD_START|" in buffer and b"|CMD_END" in buffer:
                    try:
                        # Paket başlangıcını bul
                        start_idx = buffer.find(b"CMD_START|")
                        if start_idx == -1:
                            break
                        
                        # Paket sonunu bul
                        end_idx = buffer.find(b"|CMD_END", start_idx)
                        if end_idx == -1:
                            break
                        
                        # Paketi çıkar
                        packet_data = buffer[start_idx:end_idx + 8]  # |CMD_END = 8 byte
                        buffer = buffer[end_idx + 8:]  # Kalan veriyi buffer'da tut
                        
                        # Paketi parse et
                        packet_str = packet_data.decode('utf-8', errors='ignore')
                        parts = packet_str.split('|')
                        
                        if len(parts) == 4 and parts[0] == 'CMD_START' and parts[3] == 'CMD_END':
                            command_json = parts[2]
                            command = json.loads(command_json)
                            self.handle_input(command)
                        
                    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as e:
                        print(f"⚠️ Komut parse hatası: {str(e)}")
                        break
                    except Exception as e:
                        print(f"⚠️ Komut işleme hatası: {str(e)}")
                        break
                
            except Exception as e:
                if self.running:
                    self.log(f"❌ Input alma hatası: {str(e)}")
                break
    
    def handle_input(self, command):
        """Input komutunu işle"""
        try:
            cmd_type = command.get('type')
            
            if cmd_type == 'mouse_move':
                self.input_controller.mouse_move(command['x'], command['y'])
            elif cmd_type == 'mouse_click':
                self.input_controller.mouse_click(command['button'], command['pressed'])
            elif cmd_type == 'mouse_scroll':
                self.input_controller.mouse_scroll(command['dx'], command['dy'])
            elif cmd_type == 'key_press':
                self.input_controller.key_press(command['key'], command['pressed'])
                
        except Exception as e:
            self.log(f"⚠️ Input işleme hatası: {str(e)}")
    
    def stop(self):
        """Bağlantıyı kapat"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.log("🔴 Relay bağlantısı kapatıldı")
    
    def get_id(self):
        """Host ID'yi döndür"""
        return self.host_id
