import cv2
import numpy as np
import easyocr
import pytesseract
from PIL import Image
import os

class YomitokuWrapper:
    """Yomitokuの代替OCRラッパー"""
    
    def __init__(self):
        self.use_easyocr = True
        try:
            self.easyocr_reader = easyocr.Reader(['ja', 'en'])
        except Exception as e:
            print(f"EasyOCR初期化失敗: {e}")
            self.use_easyocr = False
            
    def predict(self, image_path):
        """画像からテキストを抽出"""
        try:
            if self.use_easyocr:
                return self._extract_with_easyocr(image_path)
            else:
                return self._extract_with_tesseract(image_path)
        except Exception as e:
            print(f"OCR処理エラー: {e}")
            return ""
    
    def _extract_with_easyocr(self, image_path):
        """EasyOCRでテキスト抽出"""
        results = self.easyocr_reader.readtext(image_path)
        text_parts = []
        for (bbox, text, confidence) in results:
            if confidence > 0.5:
                text_parts.append(text)
        return ' '.join(text_parts)
    
    def _extract_with_tesseract(self, image_path):
        """Tesseractでテキスト抽出"""
        image = Image.open(image_path)
        # 日本語+英語でOCR
        text = pytesseract.image_to_string(image, lang='jpn+eng')
        return text.strip()
    
    def preprocess_image(self, image_path):
        """画像前処理"""
        image = cv2.imread(image_path)
        if image is None:
            return None
            
        # グレースケール変換
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # ノイズ除去
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # コントラスト調整
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # 保存
        processed_path = image_path.replace('.', '_processed.')
        cv2.imwrite(processed_path, enhanced)
        
        return processed_path
