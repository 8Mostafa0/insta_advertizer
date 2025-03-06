import pyautogui
import pyperclip
from time import sleep
class drive:
    def __init__(self):
        self.width,self.height = pyautogui.size()
        self.left_l = 1
        self.down_l = 1
        
    def fix_move(self,left,down):
        left+=10
        down+=10
        self.left_l = left
        self.down_l = down
        pyautogui.moveTo(left, down, duration = 1)

    def move(self,left,down,delay=True):
        if left <= 100 and 0 <= left and down <= 100 and down >= 0:
            x = int(left * (self.width / 100))
            y = int(down * (self.height / 100))
            self.left_l = x
            self.down_l = y
            self.d.hint(left,down)
            pyautogui.moveTo(x, y, duration = 1 if delay else 0)
        else:
            raise ValueError("Value must be less or equl to 100 and grate or equalt to 0")
    
    def h_click(self,left,down):
        if left <= 100 and 0 <= left and down <= 100 and down >= 0:
            x = int(left * (self.width / 100))
            y = int(down * (self.height / 100))
            pyautogui.dragTo(x,y,duration=2)
        else:
            raise ValueError("Value must be less or equl to 100 and grate or equalt to 0")

    def key_d(self,key):
        pyautogui.keyDown(key)

    def key_u(self,key):
        pyautogui.keyUp(key)

    def r_clic(self):
        pyautogui.rightClick(self.left_l,self.down_l)

    def center(self,path:str):
        x, y = pyautogui.locateCenterOnScreen(path,confidence=0.8)
        return x,y

    def click(self,path:str = ""):
        if path == "":
            pyautogui.click(self.left_l,self.down_l)
        else:
            x, y = pyautogui.locateCenterOnScreen(path,confidence=0.8)
            pyautogui.click(x, y)



    def key(self,args):
        pyautogui.keyDown(args)
        pyautogui.keyUp(args)
        # pyautogui.hotkey(args)
    
    def type(self,args):
        pyperclip.copy(args)
        pyautogui.hotkey('ctrl', 'v')
    