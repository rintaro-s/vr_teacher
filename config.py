import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # VR設定
    QUEST_IP = os.getenv("QUEST_IP", "192.168.1.100")
    QUEST_PORT = int(os.getenv("QUEST_PORT", "12346"))
    QUEST_AUDIO_PORT = int(os.getenv("QUEST_AUDIO_PORT", "12347"))
    
    # API設定
    LMSTUDIO_URL = os.getenv("LMSTUDIO_URL", "http://rinnas.f5.si:1234/v1/chat/completions")
    VOICEVOX_URL = os.getenv("VOICEVOX_URL", "http://localhost:50021")
    VOICEVOX_SPEAKER_ID = int(os.getenv("VOICEVOX_SPEAKER_ID", "58"))  # 関西弁
    
    # Discord設定
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
    DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
    
    # ディレクトリ設定
    TMP_DIR = "./tmp"
    SLIDES_DIR = "./slides"
    AUDIO_DIR = "./audio"
    MODELS_DIR = "./models"
    
    # OCR設定
    OCR_CONFIDENCE_THRESHOLD = 0.5
    OCR_LANGUAGES = ['ja', 'en']
    
    # 音声設定
    AUDIO_QUALITY = 90
    SPEECH_SPEED = 1.0
    
    # 画像設定
    IMAGE_QUALITY = 90
    SLIDE_DPI = 150
    
    # AI設定
    DEFAULT_TEMPERATURE = 0.7
    MAX_TOKENS = 2048
    
    # Pkaisetu設定
    PKAISETU_COOLDOWN = 5.0  # 秒
    PKAISETU_TIMEOUT = 30.0  # 秒
    
    @classmethod
    def create_directories(cls):
        """必要なディレクトリを作成"""
        for dir_path in [cls.TMP_DIR, cls.SLIDES_DIR, cls.AUDIO_DIR, cls.MODELS_DIR]:
            os.makedirs(dir_path, exist_ok=True)
