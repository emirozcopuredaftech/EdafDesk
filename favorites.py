"""
Favori Bağlantılar Yönetimi
"""

import json
import os
from datetime import datetime

class FavoritesManager:
    def __init__(self, file_path="favorites.json"):
        self.file_path = file_path
        self.favorites = self.load_favorites()
        
    def load_favorites(self):
        """Favorileri dosyadan yükle"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"favorites": [], "recent": []}
        return {"favorites": [], "recent": []}
    
    def save_favorites(self):
        """Favorileri dosyaya kaydet"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Kayıt hatası: {e}")
            return False
    
    def add_favorite(self, name, ip, port):
        """Yeni favori ekle"""
        favorite = {
            "name": name,
            "ip": ip,
            "port": port,
            "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Aynı IP varsa güncelle
        for i, fav in enumerate(self.favorites["favorites"]):
            if fav["ip"] == ip and fav["port"] == port:
                self.favorites["favorites"][i] = favorite
                self.save_favorites()
                return True
        
        self.favorites["favorites"].append(favorite)
        self.save_favorites()
        return True
    
    def remove_favorite(self, ip, port):
        """Favoriyi sil"""
        self.favorites["favorites"] = [
            fav for fav in self.favorites["favorites"]
            if not (fav["ip"] == ip and fav["port"] == port)
        ]
        self.save_favorites()
    
    def get_favorites(self):
        """Tüm favorileri getir"""
        return self.favorites.get("favorites", [])
    
    def add_recent(self, ip, port):
        """Son bağlantılara ekle"""
        recent = {
            "ip": ip,
            "port": port,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Aynı IP varsa eski kaydı sil
        self.favorites["recent"] = [
            r for r in self.favorites.get("recent", [])
            if not (r["ip"] == ip and r["port"] == port)
        ]
        
        # Başa ekle
        self.favorites["recent"].insert(0, recent)
        
        # Maksimum 10 kayıt tut
        self.favorites["recent"] = self.favorites["recent"][:10]
        
        self.save_favorites()
    
    def get_recent(self):
        """Son bağlantıları getir"""
        return self.favorites.get("recent", [])
