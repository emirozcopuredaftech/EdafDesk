"""
Klavye ve Fare Kontrol Modülü
"""

from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key
from PIL import ImageGrab

class InputController:
    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        
        # Ekran boyutunu al
        img = ImageGrab.grab()
        self.screen_width = img.width
        self.screen_height = img.height
    
    def move_mouse(self, rel_x, rel_y):
        """Mouse'u hareket ettir (0-1 arası oransal değerler)"""
        try:
            # Oransal değerleri piksel değerlerine çevir
            x = int(rel_x * self.screen_width)
            y = int(rel_y * self.screen_height)
            
            # Mouse'u hareket ettir
            self.mouse.position = (x, y)
        except Exception as e:
            print(f"Mouse hareket hatası: {str(e)}")
    
    def mouse_move(self, rel_x, rel_y):
        """Mouse'u hareket ettir - alias for move_mouse"""
        self.move_mouse(rel_x, rel_y)
    
    def mouse_click(self, button='left', x=None, y=None):
        """Mouse tıklaması yap - compatible method"""
        try:
            # Eğer pozisyon verilmişse önce oraya git
            if x is not None and y is not None:
                self.move_mouse(x, y)
            
            self.click_mouse(button)
        except Exception as e:
            print(f"❌ Mouse click hatası: {str(e)}")
    
    def click_mouse(self, button='left'):
        """Mouse tıklaması yap"""
        try:
            print(f"💥 TIKLANACAK: {button}")
            print(f"   Mevcut mouse pozisyonu: {self.mouse.position}")
            
            if button == 'left':
                self.mouse.click(Button.left, 1)
                print(f"   ✅ Sol tık yapıldı!")
            elif button == 'right':
                self.mouse.click(Button.right, 1)
                print(f"   ✅ Sağ tık yapıldı!")
            elif button == 'middle':
                self.mouse.click(Button.middle, 1)
                print(f"   ✅ Orta tık yapıldı!")
                
        except Exception as e:
            print(f"❌ Mouse tıklama hatası: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def press_key(self, key):
        """Klavye tuşuna bas"""
        try:
            # Özel tuşlar
            special_keys = {
                'Return': Key.enter,
                'BackSpace': Key.backspace,
                'Tab': Key.tab,
                'Escape': Key.esc,
                'space': Key.space,
                'Delete': Key.delete,
                'Home': Key.home,
                'End': Key.end,
                'Up': Key.up,
                'Down': Key.down,
                'Left': Key.left,
                'Right': Key.right,
            }
            
            if key in special_keys:
                self.keyboard.press(special_keys[key])
                self.keyboard.release(special_keys[key])
            elif len(key) == 1:
                # Normal karakter
                self.keyboard.press(key)
                self.keyboard.release(key)
                
        except Exception as e:
            print(f"Klavye basma hatası: {str(e)}")
