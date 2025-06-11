import fitz  # PyMuPDF
import os
from PIL import Image
import io

class NougatWrapper:
    """Nougatの代替PDFテキスト抽出"""
    
    def __init__(self):
        self.temp_dir = "./tmp"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def predict(self, pdf_path):
        """PDFからテキストを抽出"""
        try:
            # PDFを開く
            doc = fitz.open(pdf_path)
            text_content = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # テキスト抽出を試行
                text = page.get_text()
                if text.strip():
                    text_content.append(text)
                else:
                    # テキストが抽出できない場合、画像として処理
                    image_text = self._extract_from_image(page, page_num)
                    if image_text:
                        text_content.append(image_text)
            
            doc.close()
            return '\n'.join(text_content)
            
        except Exception as e:
            print(f"PDF処理エラー: {e}")
            return ""
    
    def _extract_from_image(self, page, page_num):
        """PDFページを画像として処理"""
        try:
            # ページを画像に変換
            mat = fitz.Matrix(2, 2)  # 2倍解像度
            pix = page.get_pixmap(matrix=mat)
            
            # 画像保存
            img_path = os.path.join(self.temp_dir, f"page_{page_num}.png")
            pix.save(img_path)
            
            # OCR処理（YomitokuWrapperを使用）
            from yomitoku_wrapper import YomitokuWrapper
            ocr = YomitokuWrapper()
            text = ocr.predict(img_path)
            
            # 一時ファイル削除
            os.remove(img_path)
            
            return text
            
        except Exception as e:
            print(f"画像処理エラー: {e}")
            return ""
