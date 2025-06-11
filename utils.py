import os
import json
import cv2
import numpy as np
from datetime import datetime
import re
import uuid

def clean_filename(filename):
    """ファイル名をクリーンアップ"""
    # 危険な文字を除去
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return cleaned[:100]  # 長さ制限

def ensure_directory(path):
    """ディレクトリが存在することを確認"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def save_json(data, filepath):
    """JSONファイル保存"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"JSON保存エラー: {e}")
        return False

def load_json(filepath):
    """JSONファイル読み込み"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"JSON読み込みエラー: {e}")
        return None

def resize_image(image_path, max_size=(1920, 1080)):
    """画像リサイズ"""
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        height, width = image.shape[:2]
        max_width, max_height = max_size
        
        # アスペクト比を保持してリサイズ
        if width > max_width or height > max_height:
            scale = min(max_width/width, max_height/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # 元ファイルを上書き
            cv2.imwrite(image_path, resized)
            
        return image_path
    except Exception as e:
        print(f"画像リサイズエラー: {e}")
        return None

def generate_unique_filename(extension):
    """ユニークなファイル名生成"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}.{extension}"

def extract_math_expressions(text):
    """テキストから数式を抽出"""
    # 数式パターン
    patterns = [
        r'[x-z]\s*[²³⁴⁵⁶⁷⁸⁹]',  # 累乗
        r'[x-z]\s*\^\s*\d+',        # x^2 形式
        r'\d*[x-z]\s*[+\-]\s*\d+',   # 一次式
        r'[x-z]\s*=\s*\d+',         # 解
        r'\d+\s*[x-z]\s*[+\-]\s*\d+\s*=\s*\d+',  # 方程式
    ]
    
    expressions = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        expressions.extend(matches)
    
    return list(set(expressions))  # 重複除去

def format_math_problem(problem_text):
    """数学問題を整形"""
    # 改行を適切に処理
    formatted = problem_text.replace('\n', ' ').strip()
    
    # 余分な空白を削除
    formatted = re.sub(r'\s+', ' ', formatted)
    
    # 数式の前後にスペースを追加
    formatted = re.sub(r'([x-z])(\d)', r'\1 \2', formatted)
    formatted = re.sub(r'(\d)([x-z])', r'\1 \2', formatted)
    
    return formatted

def validate_image_file(filepath):
    """画像ファイルの検証"""
    if not os.path.exists(filepath):
        return False, "ファイルが存在しません"
    
    # ファイルサイズチェック
    file_size = os.path.getsize(filepath)
    if file_size > 10 * 1024 * 1024:  # 10MB制限
        return False, "ファイルサイズが大きすぎます"
    
    # 画像として読み込み可能かチェック
    try:
        image = cv2.imread(filepath)
        if image is None:
            return False, "画像ファイルとして読み込めません"
    except Exception as e:
        return False, f"画像読み込みエラー: {e}"
    
    return True, "OK"

def create_thumbnail(image_path, size=(300, 300)):
    """サムネイル作成"""
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        # アスペクト比を保持してリサイズ
        height, width = image.shape[:2]
        scale = min(size[0]/width, size[1]/height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        thumbnail = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # サムネイルファイル名
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        thumb_path = os.path.join(os.path.dirname(image_path), f"{base_name}_thumb.jpg")
        
        cv2.imwrite(thumb_path, thumbnail)
        return thumb_path
        
    except Exception as e:
        print(f"サムネイル作成エラー: {e}")
        return None
