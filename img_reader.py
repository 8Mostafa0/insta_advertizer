import pytesseract
import pyautogui
from python_imagesearch.imagesearch import *
class reader:
    def __init__(self):
        self.width,self.height = pyautogui.size()
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'