"""
Host Sunucu Modülü - Ekranı Paylaşan Taraf
"""

import socket
import threading
import time
import pickle
import zlib
from screen_capture import ScreenCapture
from input_control import InputController
from config import *

class HostServer:
    def __init__(self, port, log_callback=None, approval_callback=None):
        self.port = port
        self.log = log_callback or print
        self.approval_callback = approval_callback
        self.running = False
        self.server_socket = None
        self.screen_capture = ScreenCapture()
        self.input_controller = InputController()
        self.clients = []
        
    def start(self):
        """Sunucuyu başlat"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(MAX_CONNECTIONS)
            self.running = True
            
            self.log(f"🎯 Sunucu {self.port} portunda dinliyor...")
            
            # Client kabul thread'i
            accept_thread = threading.Thread(target=self.accept_clients, daemon=True)
            accept_thread.start()
            
        except Exception as e:
            self.log(f"❌ Sunucu başlatılamadı: {str(e)}")
            self.running = False
    
    def accept_clients(self):
        """Client bağlantılarını kabul et"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                self.log(f"🔔 Bağlantı isteği: {address[0]}")
                
                # Onay callback varsa kullan
                approved = True
                if self.approval_callback:
                    try:
                        approved = self.approval_callback(address[0])
                    except Exception as e:
                        self.log(f"⚠️ Bağlantı kabul hatası: {str(e)}")
                        approved = True  # Hata durumunda kabul et
                
                if not approved:
                    self.log(f"❌ Bağlantı reddedildi: {address[0]}")
                    try:
                        client_socket.send(b"REJECTED")
                        client_socket.close()
                    except:
                        pass
                    continue
                else:
                    self.log(f"✅ Bağlantı onaylandı: {address[0]}")
                    try:
                        client_socket.send(b"APPROVED")
                    except:
                        pass
                
                # Her client için ayrı thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    self.log(f"⚠️ Bağlantı kabul hatası: {str(e)}")
    
    def handle_client(self, client_socket, address):
        """Client ile iletişimi yönet"""
        self.clients.append(client_socket)
        
        # Ekran gönderme thread'i
        screen_thread = threading.Thread(
            target=self.send_screen,
            args=(client_socket,),
            daemon=True
        )
        screen_thread.start()
        
        # Komut alma loop'u
        try:
            while self.running:
                try:
                    self.socket.settimeout(5.0)  # Timeout ayarla
                    data = client_socket.recv(BUFFER_SIZE)
                    if not data:
                        break
                    
                    # Client'tan gelen komutları işle (klavye/fare)
                    try:
                        print(f"📦 Veri alındı, boyut: {len(data)}")
                        command = pickle.loads(data)
                        print(f"📋 Deserialize edildi: {command}")
                        self.process_command(command)
                    except (pickle.UnpicklingError, ValueError) as e:
                        print(f"⚠️ Komut deserialize hatası: {str(e)}")
                        continue
                    except Exception as e:
                        print(f"⚠️ Komut işleme hatası: {str(e)}")
                        continue
                        
                except socket.timeout:
                    continue  # Timeout normale, devam et
                except (ConnectionResetError, BrokenPipeError):
                    break  # Bağlantı koptu
                    
        except Exception as e:
            self.log(f"⚠️ Client bağlantı hatası: {str(e)}")
        finally:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            client_socket.close()
            self.log(f"❌ {address} bağlantısı kesildi")
    
    def send_screen(self, client_socket):
        """Ekran görüntüsünü sürekli gönder"""
        frame_delay = 1.0 / FPS
        
        while self.running and client_socket in self.clients:
            try:
                # Ekran yakala
                screen_data = self.screen_capture.capture()
                
                if screen_data and len(screen_data) > 10:  # Veri bütünlüğü kontrolü
                    try:
                        # Veriyi sıkıştır ve gönder
                        compressed_data = zlib.compress(screen_data, 6)
                        
                        # Boyut kontrolü
                        if len(compressed_data) > MAX_FRAME_SIZE:
                            continue  # Çok büyük frame'i atla
                        
                        # Veri boyutunu gönder (4 byte)
                        size = len(compressed_data)
                        client_socket.sendall(size.to_bytes(4, byteorder='big'))
                        
                        # Veriyi gönder
                        client_socket.sendall(compressed_data)
                        
                    except (socket.error, BrokenPipeError) as e:
                        self.log(f"⚠️ Veri gönderme hatası: {str(e)}")
                        break
                    except Exception as e:
                        self.log(f"⚠️ Sıkıştırma hatası: {str(e)}")
                        continue
                
                time.sleep(frame_delay)
                
            except Exception as e:
                break
    
    def process_command(self, command):
        """Client'tan gelen komutları işle"""
        print(f"🔥 KOMUT ALINDI: {command}")
        
        cmd_type = command.get('type')
        
        if cmd_type == 'mouse_move':
            x, y = command.get('x', 0), command.get('y', 0)
            print(f"   → Mouse move: ({x}, {y})")
            self.input_controller.move_mouse(x, y)
            
        elif cmd_type == 'mouse_click':
            button = command.get('button', 'left')
            # Pozisyon bilgisi varsa önce mouse'u taşı
            if 'x' in command and 'y' in command:
                x, y = command.get('x'), command.get('y')
                print(f"   → Mouse pozisyonunu taşı: ({x:.2f}, {y:.2f})")
                self.input_controller.move_mouse(x, y)
            print(f"   → Mouse click: {button}")
            self.input_controller.click_mouse(button)
            
        elif cmd_type == 'key_press':
            key = command.get('key', '')
            print(f"   → Key press: {key}")
            self.input_controller.press_key(key)
    
    def stop(self):
        """Sunucuyu durdur"""
        self.running = False
        
        # Tüm client bağlantılarını kapat
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        
        # Sunucu socket'ini kapat
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        self.log("⏹ Host sunucusu durduruldu")
