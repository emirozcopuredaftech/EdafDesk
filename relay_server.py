"""
Relay Sunucu - Anydesk tarzı merkezi sunucu
Host ve Client arasında köprü görevi görür
"""

import socket
import threading
import random
import time
import struct

class RelayServer:
    def __init__(self, port=9999):
        self.port = port
        self.hosts = {}  # {id: socket}
        self.clients = {}  # {id: [socket1, socket2, ...]}
        self.running = False
        self.lock = threading.Lock()
        
    def generate_id(self):
        """Benzersiz 9 haneli ID üret"""
        while True:
            new_id = random.randint(100000000, 999999999)
            if new_id not in self.hosts:
                return new_id
    
    def start(self):
        """Sunucuyu başlat"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(100)
            self.running = True
            
            print(f"🚀 Relay sunucu {self.port} portunda başlatıldı")
            
            while self.running:
                client_socket, address = self.server_socket.accept()
                print(f"📞 Yeni bağlantı: {address}")
                
                thread = threading.Thread(
                    target=self.handle_connection,
                    args=(client_socket, address),
                    daemon=True
                )
                thread.start()
                
        except Exception as e:
            print(f"❌ Sunucu hatası: {e}")
        finally:
            self.running = False
            if hasattr(self, 'server_socket'):
                self.server_socket.close()
    
    def handle_connection(self, conn, address):
        """Bağlantıyı yönet"""
        try:
            # İlk mesaj: TYPE belirleme (HOST/CLIENT)
            conn.settimeout(10)
            type_msg = conn.recv(1024).decode().strip()
            
            if type_msg == "HOST":
                self.handle_host(conn, address)
            elif type_msg.startswith("CLIENT:"):
                host_id = int(type_msg.split(":")[1])
                self.handle_client(conn, address, host_id)
            else:
                print(f"⚠️ Bilinmeyen tip: {type_msg}")
                conn.close()
                
        except Exception as e:
            print(f"❌ Bağlantı hatası {address}: {e}")
            conn.close()
    
    def handle_host(self, conn, address):
        """Host bağlantısını yönet"""
        host_id = self.generate_id()
        
        with self.lock:
            self.hosts[host_id] = conn
            self.clients[host_id] = []
        
        # Host'a ID'sini gönder
        conn.send(f"ID:{host_id}".encode())
        print(f"🎯 Host kaydedildi - ID: {host_id} ({address})")
        
        try:
            while self.running:
                # Host'tan veri al (ekran görüntüsü)
                data_size_bytes = conn.recv(4)
                if not data_size_bytes:
                    break
                
                data_size = struct.unpack('!I', data_size_bytes)[0]
                
                # Veriyi al
                data = b''
                while len(data) < data_size:
                    packet = conn.recv(min(65536, data_size - len(data)))
                    if not packet:
                        break
                    data += packet
                
                # Tüm client'lara ilet
                with self.lock:
                    dead_clients = []
                    for client_conn in self.clients.get(host_id, []):
                        try:
                            client_conn.send(data_size_bytes)
                            client_conn.send(data)
                        except:
                            dead_clients.append(client_conn)
                    
                    # Ölü client'ları temizle
                    for dead in dead_clients:
                        if dead in self.clients[host_id]:
                            self.clients[host_id].remove(dead)
                            
        except Exception as e:
            print(f"❌ Host hatası {host_id}: {e}")
        finally:
            with self.lock:
                if host_id in self.hosts:
                    del self.hosts[host_id]
                if host_id in self.clients:
                    for client_conn in self.clients[host_id]:
                        try:
                            client_conn.close()
                        except:
                            pass
                    del self.clients[host_id]
            conn.close()
            print(f"🔴 Host ayrıldı: {host_id}")
    
    def handle_client(self, conn, address, host_id):
        """Client bağlantısını yönet"""
        with self.lock:
            if host_id not in self.hosts:
                conn.send(b"ERROR:HOST_NOT_FOUND")
                conn.close()
                print(f"⚠️ Host bulunamadı: {host_id}")
                return
            
            self.clients[host_id].append(conn)
            conn.send(b"OK:CONNECTED")
        
        print(f"✅ Client bağlandı - Host ID: {host_id} ({address})")
        
        try:
            # Client'tan input komutlarını al ve host'a ilet
            host_conn = self.hosts.get(host_id)
            if not host_conn:
                return
                
            while self.running:
                data = conn.recv(4096)
                if not data:
                    break
                
                # Input komutunu host'a ilet
                try:
                    host_conn.send(data)
                except:
                    break
                    
        except Exception as e:
            print(f"❌ Client hatası: {e}")
        finally:
            with self.lock:
                if host_id in self.clients and conn in self.clients[host_id]:
                    self.clients[host_id].remove(conn)
            conn.close()
            print(f"🔴 Client ayrıldı: {host_id}")

if __name__ == "__main__":
    server = RelayServer(port=9999)
    print("=" * 50)
    print("EdafDesk Relay Server")
    print("=" * 50)
    server.start()
