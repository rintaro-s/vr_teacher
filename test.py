import sys
import importlib
import subprocess
from pathlib import Path
import json
import os
import warnings

# 警告を抑制
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # TensorFlow警告抑制
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # oneDNN警告抑制

class LibraryChecker:
    def __init__(self):
        self.required_libraries = {
            # 基本ライブラリ
            'cv2': 'opencv-python',
            'numpy': 'numpy',
            'torch': 'torch',
            'transformers': 'transformers',
            'easyocr': 'easyocr',
            'PIL': 'Pillow',
            'aiohttp': 'aiohttp',
            'requests': 'requests',
            'discord': 'discord.py',
            'llama_cpp': 'llama-cpp-python',
            
            # 音声関連
            'uvicorn': 'uvicorn',
            'fastapi': 'fastapi',
            
            # システム情報
            'psutil': 'psutil',
            'GPUtil': 'GPUtil',
            
            # 専用ライブラリ（オプション）
            'nougat': 'nougat-ocr',
            'yomitoku': 'yomitoku',
        }
        
        self.missing_libraries = []
        self.optional_missing = []
        self.loaded_libraries = []
        self.failed_optional = []
        
    def check_library(self, module_name, package_name, optional=False):
        """ライブラリの読み込みチェック"""
        try:
            # 標準出力をキャプチャして警告を抑制
            import io
            from contextlib import redirect_stderr, redirect_stdout
            
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                if module_name == 'cv2':
                    import cv2
                    print(f"[OK] OpenCV: {cv2.__version__}")
                elif module_name == 'torch':
                    import torch
                    print(f"[OK] PyTorch: {torch.__version__}")
                    if torch.cuda.is_available():
                        device_name = torch.cuda.get_device_name(0)
                        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                        print(f"     CUDA Available: {device_name} ({gpu_memory:.1f}GB)")
                    else:
                        print("     CUDA: Not Available")
                elif module_name == 'transformers':
                    import transformers
                    print(f"[OK] Transformers: {transformers.__version__}")
                elif module_name == 'llama_cpp':
                    from llama_cpp import Llama
                    print(f"[OK] Llama-cpp-python: Available")
                elif module_name == 'easyocr':
                    import easyocr
                    print(f"[OK] EasyOCR: Available")
                elif module_name == 'PIL':
                    from PIL import Image
                    print(f"[OK] Pillow: Available")
                elif module_name == 'discord':
                    import discord
                    print(f"[OK] Discord.py: {discord.__version__}")
                elif module_name == 'fastapi':
                    import fastapi
                    print(f"[OK] FastAPI: {fastapi.__version__}")
                elif module_name == 'uvicorn':
                    import uvicorn
                    print(f"[OK] Uvicorn: Available")
                elif module_name == 'psutil':
                    import psutil
                    print(f"[OK] Psutil: {psutil.__version__}")
                elif module_name == 'GPUtil':
                    import GPUtil
                    print(f"[OK] GPUtil: Available")
                elif module_name == 'nougat':
                    # Nougatは特別にハンドリング
                    try:
                        from nougat import NougatModel
                        print(f"[OK] Nougat: Available (Optional)")
                    except Exception as nougat_error:
                        if "compression_type" in str(nougat_error) or "validation error" in str(nougat_error):
                            print(f"[WARN] Nougat: Version compatibility issue (Optional)")
                            print(f"       Suggestion: pip install nougat-ocr==0.1.17")
                            self.failed_optional.append((package_name, "Version compatibility"))
                            return True  # 存在はするが問題あり
                        else:
                            raise nougat_error
                elif module_name == 'yomitoku':
                    import yomitoku
                    print(f"[OK] Yomitoku: Available (Optional)")
                else:
                    importlib.import_module(module_name)
                    print(f"[OK] {module_name}: Available")
                
            self.loaded_libraries.append(package_name)
            return True
            
        except ImportError as e:
            if optional:
                print(f"[SKIP] {module_name}: Not installed (Optional)")
                self.optional_missing.append(package_name)
            else:
                print(f"[FAIL] {module_name}: Not installed")
                self.missing_libraries.append(package_name)
            return False
        except Exception as e:
            error_msg = str(e)
            if optional:
                print(f"[WARN] {module_name}: Error loading (Optional)")
                print(f"       {error_msg[:80]}...")
                self.failed_optional.append((package_name, error_msg[:50]))
            else:
                print(f"[FAIL] {module_name}: Error loading")
                print(f"       {error_msg[:80]}...")
                self.missing_libraries.append(package_name)
            return False
    
    def check_models(self):
        """モデルファイルの存在チェック"""
        print("\n[MODEL CHECK] Scanning GGUF models...")
        
        try:
            from config import scan_available_models
            
            # 利用可能なモデルをスキャン
            available_models = scan_available_models()
            
            if available_models:
                total_size = sum(model['size_gb'] for model in available_models)
                print(f"[OK] Found {len(available_models)} GGUF models (Total: {total_size:.1f}GB)")
                
                # サイズ別にソート
                sorted_models = sorted(available_models, key=lambda x: x['size_gb'], reverse=True)
                
                print("     Top 5 largest models:")
                for model in sorted_models[:5]:
                    print(f"       - {model['name'][:40]:<40} ({model['size_gb']:>5.1f}GB)")
                
                if len(available_models) > 5:
                    print(f"       ... and {len(available_models) - 5} more models")
                    
            else:
                print("[FAIL] No GGUF models found")
                print("       Please place .gguf files in the models directory")
                
        except ImportError:
            print("[FAIL] config.py not found")
        except Exception as e:
            print(f"[FAIL] Model scan error: {e}")
    
    def check_services(self):
        """外部サービスの接続チェック"""
        print("\n[SERVICE CHECK] Testing external services...")
        
        try:
            import requests
            
            # VoiceVox接続チェック
            try:
                response = requests.get("http://127.0.0.1:50021/version", timeout=3)
                if response.status_code == 200:
                    version_info = response.json()
                    version = version_info.get('version', 'unknown')
                    print(f"[OK] VoiceVox: Running (v{version})")
                else:
                    print("[FAIL] VoiceVox: Server responded with error")
            except requests.exceptions.ConnectionError:
                print("[FAIL] VoiceVox: Server not running")
                print("       Start VoiceVox before running the main application")
            except requests.exceptions.Timeout:
                print("[WARN] VoiceVox: Connection timeout")
            except Exception as e:
                print(f"[FAIL] VoiceVox: {str(e)[:50]}...")
                
        except ImportError:
            print("[FAIL] requests library not available")
    
    def check_system_requirements(self):
        """システム要件チェック"""
        print("\n[SYSTEM CHECK] Verifying system requirements...")
        
        try:
            import psutil
            
            # メモリチェック
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            print(f"[INFO] System Memory: {memory_gb:.1f}GB")
            
            if memory_gb < 8:
                print("[WARN] Insufficient memory (Recommended: 8GB+)")
            elif memory_gb < 16:
                print("[OK] Memory adequate for basic models")
            else:
                print("[OK] Memory sufficient for large models")
                
            # CPU情報
            cpu_count = psutil.cpu_count()
            print(f"[INFO] CPU Cores: {cpu_count}")
            
            # ディスク使用量チェック
            try:
                models_path = Path("./models")
                if models_path.exists():
                    total_size = sum(f.stat().st_size for f in models_path.rglob("*") if f.is_file())
                    total_size_gb = total_size / (1024**3)
                    print(f"[INFO] Models Directory: {total_size_gb:.1f}GB")
                else:
                    print("[WARN] Models directory not found")
            except Exception:
                pass
                
        except ImportError:
            print("[FAIL] psutil not available")
            
        # Python バージョンチェック
        python_version = sys.version_info
        version_str = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
        print(f"[INFO] Python Version: {version_str}")
        
        if python_version < (3, 8):
            print("[WARN] Python 3.8+ recommended")
        elif python_version >= (3, 12):
            print("[WARN] Python 3.12+ may have compatibility issues")
        else:
            print("[OK] Python version compatible")
    
    def run_all_checks(self):
        """すべてのチェックを実行"""
        print("=" * 60)
        print("HOMEWORK HELPER - SYSTEM CHECK")
        print("=" * 60)
        
        print("\n[ESSENTIAL LIBRARIES]")
        essential_libraries = ['cv2', 'numpy', 'torch', 'transformers', 'easyocr', 'PIL', 'aiohttp', 'requests', 'discord', 'llama_cpp', 'fastapi', 'uvicorn', 'psutil']
        
        for lib in essential_libraries:
            if lib in self.required_libraries:
                self.check_library(lib, self.required_libraries[lib])
        
        print("\n[OPTIONAL LIBRARIES]")
        optional_libraries = ['GPUtil', 'nougat', 'yomitoku']
        
        for lib in optional_libraries:
            if lib in self.required_libraries:
                self.check_library(lib, self.required_libraries[lib], optional=True)
        
        # その他のチェック
        self.check_models()
        self.check_services()
        self.check_system_requirements()
        
        # 結果サマリー
        self.print_summary()
    
    def print_summary(self):
        """チェック結果のサマリーを表示"""
        print("\n" + "=" * 60)
        print("SUMMARY REPORT")
        print("=" * 60)
        
        # 成功統計
        total_essential = 13  # 必須ライブラリの数
        loaded_essential = total_essential - len(self.missing_libraries)
        
        print(f"Essential Libraries: {loaded_essential}/{total_essential} loaded")
        print(f"Optional Libraries:  {len(self.loaded_libraries) - loaded_essential} loaded")
        print(f"Failed Libraries:    {len(self.missing_libraries)} missing")
        
        # 不足ライブラリがある場合
        if self.missing_libraries:
            print(f"\n[MISSING LIBRARIES]")
            for lib in self.missing_libraries:
                print(f"  - {lib}")
                
            print(f"\n[INSTALL COMMAND]")
            install_cmd = "pip install " + " ".join(self.missing_libraries)
            print(f"  {install_cmd}")
            
            # 特別な指示
            if any('torch' in lib for lib in self.missing_libraries):
                print(f"\n[CUDA PyTorch (if needed)]")
                print(f"  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124")
                
            if any('llama-cpp' in lib for lib in self.missing_libraries):
                print(f"\n[CUDA llama-cpp-python (if needed)]")
                print(f"  pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124")
        
        # オプションライブラリの問題
        if self.optional_missing:
            print(f"\n[OPTIONAL MISSING]")
            for lib in self.optional_missing:
                print(f"  - {lib}")
            optional_cmd = "pip install " + " ".join(self.optional_missing)
            print(f"\n[OPTIONAL INSTALL COMMAND]")
            print(f"  {optional_cmd}")
        
        # 問題のあるオプションライブラリ
        if self.failed_optional:
            print(f"\n[OPTIONAL ISSUES]")
            for lib, error in self.failed_optional:
                print(f"  - {lib}: {error}")
        
        # 全体的な状態
        print(f"\n[OVERALL STATUS]")
        if not self.missing_libraries:
            if not self.failed_optional:
                print("  STATUS: READY - All systems operational!")
            else:
                print("  STATUS: MOSTLY READY - Minor optional issues")
        else:
            print("  STATUS: NOT READY - Install missing libraries")
        
        print(f"\n[NEXT STEPS]")
        if not self.missing_libraries:
            print("  1. Configure Discord Bot Token (config.py)")
            print("  2. Set VR device IP address (config.py)")
            print("  3. Start VoiceVox server")
            print("  4. Run: python main.py")
        else:
            print("  1. Install missing libraries (see commands above)")
            print("  2. Re-run this test")
            print("  3. Configure settings in config.py")
        
        print("=" * 60)

def main():
    """メイン実行関数"""
    checker = LibraryChecker()
    
    try:
        checker.run_all_checks()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Check cancelled by user")
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error occurred: {e}")
        print("\nDetailed error information:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
