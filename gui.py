"""
GUI Arayüzü - Ana Pencere
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import threading
import socket
from config import *
from host import HostServer
from client import ClientConnection
from favorites import FavoritesManager

class RemoteDesktopGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EdafDesk - Uzak Masaüstü")
        self.root.geometry("700x800")
        self.root.configure(bg=BG_COLOR)
        
        self.host_server = None
        self.client_connection = None
        self.favorites_manager = FavoritesManager()
        
        self.setup_ui()
        self.get_local_ip()
        self.load_favorites_list()
        
    def setup_ui(self):
        """UI Bileşenlerini oluştur"""
        # Başlık
        title_frame = tk.Frame(self.root, bg=PRIMARY_COLOR)
        title_frame.pack(fill=tk.X, pady=0)
        
        title_label = tk.Label(
            title_frame,
            text="EdafDesk",
            font=("Arial", 24, "bold"),
            bg=PRIMARY_COLOR,
            fg="white",
            pady=20
        )
        title_label.pack()
        
        # Ana Container
        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # HOST BÖLÜMÜ
        host_frame = tk.LabelFrame(
            main_frame,
            text="🖥️ Ekranımı Paylaş (Host)",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            pady=10,
            padx=10
        )
        host_frame.pack(fill=tk.X, pady=(0, 20))
        
        # IP Bilgisi
        ip_frame = tk.Frame(host_frame, bg=BG_COLOR)
        ip_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            ip_frame,
            text="IP Adresiniz:",
            font=("Arial", 10),
            bg=BG_COLOR
        ).pack(side=tk.LEFT)
        
        self.ip_label = tk.Label(
            ip_frame,
            text="Yükleniyor...",
            font=("Arial", 10, "bold"),
            bg=BG_COLOR,
            fg=PRIMARY_COLOR
        )
        self.ip_label.pack(side=tk.LEFT, padx=10)
        
        # Port
        port_frame = tk.Frame(host_frame, bg=BG_COLOR)
        port_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            port_frame,
            text="Port:",
            font=("Arial", 10),
            bg=BG_COLOR
        ).pack(side=tk.LEFT)
        
        self.port_entry = tk.Entry(port_frame, font=("Arial", 10), width=10)
        self.port_entry.insert(0, str(DEFAULT_PORT))
        self.port_entry.pack(side=tk.LEFT, padx=10)
        
        # Host Butonları
        self.start_host_btn = tk.Button(
            host_frame,
            text="▶ Ekran Paylaşımını Başlat",
            font=("Arial", 11, "bold"),
            bg=SUCCESS_COLOR,
            fg="white",
            command=self.start_host,
            cursor="hand2",
            pady=10
        )
        self.start_host_btn.pack(fill=tk.X, pady=5)
        
        self.stop_host_btn = tk.Button(
            host_frame,
            text="⏹ Ekran Paylaşımını Durdur",
            font=("Arial", 11, "bold"),
            bg=ERROR_COLOR,
            fg="white",
            command=self.stop_host,
            cursor="hand2",
            pady=10,
            state=tk.DISABLED
        )
        self.stop_host_btn.pack(fill=tk.X, pady=5)
        
        # CLIENT BÖLÜMÜ
        client_frame = tk.LabelFrame(
            main_frame,
            text="🔌 Uzak Bilgisayara Bağlan (Client)",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            pady=10,
            padx=10
        )
        client_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Favori seçimi
        fav_select_frame = tk.Frame(client_frame, bg=BG_COLOR)
        fav_select_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            fav_select_frame,
            text="Favoriler:",
            font=("Arial", 10),
            bg=BG_COLOR
        ).pack(side=tk.LEFT)
        
        self.favorites_combo = ttk.Combobox(
            fav_select_frame,
            font=("Arial", 10),
            width=30,
            state="readonly"
        )
        self.favorites_combo.pack(side=tk.LEFT, padx=10)
        self.favorites_combo.bind("<<ComboboxSelected>>", self.on_favorite_selected)
        
        # Hedef IP
        target_frame = tk.Frame(client_frame, bg=BG_COLOR)
        target_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            target_frame,
            text="IP Adresi:",
            font=("Arial", 10),
            bg=BG_COLOR
        ).pack(side=tk.LEFT)
        
        self.target_ip_entry = tk.Entry(target_frame, font=("Arial", 10), width=20)
        self.target_ip_entry.insert(0, "192.168.1.100")
        self.target_ip_entry.pack(side=tk.LEFT, padx=10)
        
        # Hedef Port
        target_port_frame = tk.Frame(client_frame, bg=BG_COLOR)
        target_port_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            target_port_frame,
            text="Port:",
            font=("Arial", 10),
            bg=BG_COLOR
        ).pack(side=tk.LEFT)
        
        self.target_port_entry = tk.Entry(target_port_frame, font=("Arial", 10), width=10)
        self.target_port_entry.insert(0, str(DEFAULT_PORT))
        self.target_port_entry.pack(side=tk.LEFT, padx=10)
        
        # Client Butonları
        buttons_frame = tk.Frame(client_frame, bg=BG_COLOR)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        self.connect_btn = tk.Button(
            buttons_frame,
            text="🔗 Bağlan",
            font=("Arial", 11, "bold"),
            bg=PRIMARY_COLOR,
            fg="white",
            command=self.connect_to_host,
            cursor="hand2",
            pady=10
        )
        self.connect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.save_fav_btn = tk.Button(
            buttons_frame,
            text="⭐ Kaydet",
            font=("Arial", 11, "bold"),
            bg=SUCCESS_COLOR,
            fg="white",
            command=self.save_favorite,
            cursor="hand2",
            pady=10
        )
        self.save_fav_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.disconnect_btn = tk.Button(
            buttons_frame,
            text="❌ Kes",
            font=("Arial", 11, "bold"),
            bg=ERROR_COLOR,
            fg="white",
            command=self.disconnect_from_host,
            cursor="hand2",
            pady=10,
            state=tk.DISABLED
        )
        self.disconnect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # LOG BÖLÜMÜ
        log_frame = tk.LabelFrame(
            main_frame,
            text="📋 Durum Logları",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            pady=10,
            padx=10
        )
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 9),
            height=10,
            bg="#F5F5F5"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log("EdafDesk başlatıldı.")
        
    def get_local_ip(self):
        """Yerel IP adresini al"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            self.ip_label.config(text=ip)
            self.log(f"Yerel IP: {ip}")
        except Exception as e:
            self.ip_label.config(text="Bulunamadı")
            self.log(f"IP alınamadı: {str(e)}")
    
    def log(self, message):
        """Log mesajı ekle"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        
    def start_host(self):
        """Host sunucusunu başlat"""
        try:
            port = int(self.port_entry.get())
            self.host_server = HostServer(port, self.log, self.approval_dialog)
            
            # Sunucuyu ayrı thread'de başlat
            host_thread = threading.Thread(target=self.host_server.start, daemon=True)
            host_thread.start()
            
            self.start_host_btn.config(state=tk.DISABLED)
            self.stop_host_btn.config(state=tk.NORMAL)
            self.log(f"✅ Host sunucusu başlatıldı (Port: {port})")
            
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir port numarası girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Host başlatılamadı: {str(e)}")
            self.log(f"❌ Hata: {str(e)}")
    
    def approval_dialog(self, ip_address):
        """Bağlantı onay dialogu"""
        result = messagebox.askyesno(
            "Bağlantı İsteği",
            f"⚠️ {ip_address} adresi bağlanmak istiyor.\n\nBağlantıyı onaylıyor musunuz?",
            icon='question'
        )
        return result
    
    def stop_host(self):
        """Host sunucusunu durdur"""
        if self.host_server:
            self.host_server.stop()
            self.host_server = None
            
            self.start_host_btn.config(state=tk.NORMAL)
            self.stop_host_btn.config(state=tk.DISABLED)
            self.log("⏹ Host sunucusu durduruldu")
    
    def connect_to_host(self):
        """Uzak host'a bağlan"""
        try:
            ip = self.target_ip_entry.get()
            port = int(self.target_port_entry.get())
            
            # Son bağlantılara ekle
            self.favorites_manager.add_recent(ip, port)
            self.load_favorites_list()
            
            self.client_connection = ClientConnection(ip, port, self.log)
            
            # Client'ı ayrı thread'de başlat
            client_thread = threading.Thread(
                target=self.client_connection.connect,
                daemon=True
            )
            client_thread.start()
            
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            self.log(f"🔗 {ip}:{port} adresine bağlanılıyor...")
            
        except ValueError:
            messagebox.showerror("Hata", "Geçerli IP ve port girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Bağlantı başlatılamadı: {str(e)}")
            self.log(f"❌ Hata: {str(e)}")
    
    def disconnect_from_host(self):
        """Bağlantıyı kes"""
        if self.client_connection:
            self.client_connection.disconnect()
            self.client_connection = None
            
            self.connect_btn.config(state=tk.NORMAL)
            self.disconnect_btn.config(state=tk.DISABLED)
            self.log("❌ Bağlantı kesildi")
    
    def save_favorite(self):
        """Mevcut bağlantıyı favorilere kaydet"""
        ip = self.target_ip_entry.get()
        port = self.target_port_entry.get()
        
        if not ip:
            messagebox.showwarning("Uyarı", "IP adresi giriniz!")
            return
        
        # İsim sor
        name = simpledialog.askstring(
            "Favori İsmi",
            f"Bu bağlantı için bir isim girin:\n{ip}:{port}",
            initialvalue=f"Bağlantı {ip}"
        )
        
        if name:
            try:
                self.favorites_manager.add_favorite(name, ip, int(port))
                self.load_favorites_list()
                self.log(f"⭐ '{name}' favorilere eklendi")
                messagebox.showinfo("Başarılı", f"'{name}' favorilere kaydedildi!")
            except Exception as e:
                messagebox.showerror("Hata", f"Kayıt başarısız: {str(e)}")
    
    def on_favorite_selected(self, event=None):
        """Favori seçildiğinde IP ve port'u doldur"""
        selection = self.favorites_combo.get()
        if not selection or selection.startswith("---"):
            return
        
        # Favorilerde ara
        for fav in self.favorites_manager.get_favorites():
            if selection.startswith(fav["name"]):
                self.target_ip_entry.delete(0, tk.END)
                self.target_ip_entry.insert(0, fav["ip"])
                self.target_port_entry.delete(0, tk.END)
                self.target_port_entry.insert(0, fav["port"])
                return
        
        # Son bağlantılarda ara
        for rec in self.favorites_manager.get_recent():
            if selection.startswith(rec["ip"]):
                self.target_ip_entry.delete(0, tk.END)
                self.target_ip_entry.insert(0, rec["ip"])
                self.target_port_entry.delete(0, tk.END)
                self.target_port_entry.insert(0, rec["port"])
                return
    
    def load_favorites_list(self):
        """Favori listesini yükle"""
        values = []
        
        # Favorileri ekle
        favorites = self.favorites_manager.get_favorites()
        if favorites:
            values.append("--- FAVORİLER ---")
            for fav in favorites:
                values.append(f"{fav['name']} ({fav['ip']}:{fav['port']})")
        
        # Son bağlantıları ekle
        recent = self.favorites_manager.get_recent()
        if recent:
            if values:
                values.append("--- SON BAĞLANTILAR ---")
            for rec in recent:
                values.append(f"{rec['ip']}:{rec['port']} ({rec['timestamp']})")
        
        self.favorites_combo['values'] = values if values else ["Favori yok"]

