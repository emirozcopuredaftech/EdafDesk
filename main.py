"""
EdafDesk - Uzak Masaüstü Uygulaması
Ana Uygulama Launcher
by Edaf
"""

import tkinter as tk
from tkinter import ttk, messagebox
from gui import RemoteDesktopGUI

def main():
    """Ana uygulama başlatıcı"""
    try:
        root = tk.Tk()
        app = RemoteDesktopGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Hata", f"Uygulama başlatılamadı: {str(e)}")

if __name__ == "__main__":
    main()
