import cv2
import base64
import requests
import socket
import threading
import time
import os
import json
import queue
import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import subprocess
import tempfile
import numpy as np
import uuid  # 追加
from config import Config
from yomitoku_wrapper import YomitokuWrapper
from nougat_wrapper import NougatWrapper
from slide import (create_slide_1, create_pkaisetu_slide, create_math_graph_slide, 
                   create_step_by_step_slide, create_celebration_slide)
from utils import validate_image_file, resize_image, extract_math_expressions  # 追加

class VRSenseiSystem:
    def __init__(self):
        # 設定読み込み
        Config.create_directories()
        self.config = Config()
        
        # 設定値を修正
        self.quest_ip = self.config.QUEST_IP
        self.quest_port = self.config.QUEST_PORT
        self.lmstudio_url = self.config.LMSTUDIO_URL
        self.voicevox_url = self.config.VOICEVOX_URL
        
        # tmp_dirも設定から取得
        self.tmp_dir = self.config.TMP_DIR
        
        # 状態管理
        self.genshori_phase = "waiting"  # waiting, processing, teaching, pkaisetu
        self.genshori_lock = threading.Lock()
        self.pkaisetu_processing = False
        self.last_pkaisetu_time = 0
        self.pkaisetu_cooldown = 5.0
        
        # データ保存
        self.tmp_dir = "./tmp"
        os.makedirs(self.tmp_dir, exist_ok=True)
        self.current_slides = []
        self.current_explanation = ""
        self.discord_history = []
        
        # カメラとソケット
        self.camera = None
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Discord Bot
        self.bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
        self.setup_discord_events()
        
        # 処理キュー
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
        # GUI
        self.gui_root = None
        self.status_text = None
        self.log_text = None
        
        # AI モデル（修正版）
        self.nougat_model = None
        self.yomitoku_model = None
        self.init_models()
        
        # コマンド認識パターン
        self.commands = {
            "restart": self.restart_explanation,
            "skip": self.skip_current_slide,
            "repeat": self.repeat_current_slide,
            "faster": self.speed_up,
            "slower": self.speed_down,
            "stop": self.stop_explanation
        }
    
    def init_models(self):
        """AIモデルの初期化（修正版）"""
        try:
            self.log("モデル初期化中...")
            self.nougat_model = NougatWrapper()
            self.yomitoku_model = YomitokuWrapper()
            self.log("モデル初期化完了")
        except Exception as e:
            self.log(f"モデル初期化エラー: {e}")
    
    def setup_discord_events(self):
        """Discord Botのイベント設定"""
        @self.bot.event
        async def on_ready():
            self.log(f'Discord Bot準備完了: {self.bot.user}')
        
        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return
            
            if message.attachments:
                await self.process_discord_attachment(message)
    
    async def process_discord_attachment(self, message):
        """Discord添付ファイルの処理"""
        try:
            attachment = message.attachments[0]
            if not attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                await message.reply("画像またはPDFファイルを送ってね！")
                return
            
            # ファイル保存
            file_path = os.path.join(self.tmp_dir, f"discord_{uuid.uuid4()}_{attachment.filename}")
            await attachment.save(file_path)
            
            # ファイル検証
            if not attachment.filename.lower().endswith('.pdf'):
                is_valid, error_msg = validate_image_file(file_path)
                if not is_valid:
                    await message.reply(f"ファイルエラー: {error_msg}")
                    return
                
                # 画像リサイズ
                resize_image(file_path)
            
            self.discord_history.append({
                'file_path': file_path,
                'timestamp': datetime.now(),
                'user': str(message.author)
            })
            
            await message.reply("画像を受け取ったよ！解説を作ってるから少し待ってね～♪")
            
            # 非同期処理開始
            threading.Thread(target=self.process_homework_image, args=(file_path,), daemon=True).start()
            
        except Exception as e:
            self.log(f"Discord処理エラー: {e}")
            await message.reply("エラーが発生したよ～ごめんね！")
    
    def process_homework_image(self, image_path):
        """宿題画像の処理"""
        with self.genshori_lock:
            if self.genshori_phase != "waiting":
                self.log("他の処理中のためスキップ")
                return
            
            self.genshori_phase = "processing"
        
        try:
            self.log("宿題画像処理開始")
            self.update_gui_status("画像解析中...")
            
            # Step 1: OCR/Nougat処理
            text_content = self.extract_text_from_image(image_path)
            
            # Step 2: 問題文理解・テキスト化
            self.update_gui_status("問題文解析中...")
            structured_problems = self.analyze_problems(text_content, image_path)
            
            # Step 3: 解説生成
            self.update_gui_status("解説生成中...")
            explanation = self.generate_explanation(structured_problems)
            
            # Step 4: スライド作成
            self.update_gui_status("スライド作成中...")
            slides = self.create_slides(explanation)
            
            self.current_slides = slides
            self.current_explanation = explanation
            
            # Step 5: VR準備完了通知
            self.genshori_phase = "teaching"
            self.update_gui_status("VR準備完了")
            self.log("解説準備完了！VRで「おしえて！」と書いてね")
            
        except Exception as e:
            self.log(f"処理エラー: {e}")
            self.genshori_phase = "waiting"
            self.update_gui_status("エラー発生")
    
    def extract_text_from_image(self, image_path):
        """画像からテキスト抽出"""
        try:
            if image_path.lower().endswith('.pdf'):
                # Nougat for PDF
                return self.nougat_model.predict(image_path)
            else:
                # Yomitoku for images
                return self.yomitoku_model.predict(image_path)
        except Exception as e:
            self.log(f"テキスト抽出エラー: {e}")
            return ""
    
    def analyze_problems(self, text_content, image_path):
        """問題文の解析・構造化"""
        prompt = f"""この画像と抽出されたテキストから、数学の問題を正確に理解して構造化してください。

抽出テキスト:
{text_content}

以下の形式でJSONで返してください:
{{
    "problems": [
        {{
            "problem_number": "問題番号",
            "problem_text": "問題文",
            "problem_type": "問題の種類",
            "difficulty": "難易度"
        }}
    ]
}}"""
        
        return self.call_vlm("gemma-3-12b-it", prompt, image_path)
    
    def generate_explanation(self, problems_json):
        """解説生成"""
        prompt = f"""以下の数学問題について、妹キャラとして分かりやすく解説を作成してください。

問題情報:
{problems_json}

要求:
- 妹口調で親しみやすく
- ステップバイステップで丁寧に
- 途中式も含めて
- 「お兄ちゃん」呼び
- 励ましの言葉も含める

解説形式:
1. 問題の確認
2. 解法の説明
3. 計算過程
4. 答えの確認
5. まとめ"""
        
        return self.call_llm("japanese-starling-chatv-7b", prompt)
    
    def create_slides(self, explanation):
        """スライド作成（修正版）"""
        try:
            slides = []
            
            # メインスライド作成
            create_slide_1()
            main_slide = os.path.join(self.config.TMP_DIR, "slide_0.png")
            if os.path.exists(main_slide):
                slides.append(main_slide)
            
            # 解説からステップを抽出してスライド作成
            steps = self._extract_steps_from_explanation(explanation)
            for i, step in enumerate(steps, 1):
                create_step_by_step_slide(i, step)
                step_slide = os.path.join(self.config.TMP_DIR, f"step_{i}_slide.png")
                if os.path.exists(step_slide):
                    slides.append(step_slide)
            
            # グラフスライド作成（数学問題の場合）
            if self._is_math_problem(explanation):
                create_math_graph_slide("x² - 5x + 6 = 0")
                graph_slide = os.path.join(self.config.TMP_DIR, "graph_slide.png")
                if os.path.exists(graph_slide):
                    slides.append(graph_slide)
            
            # 完了スライド
            create_celebration_slide()
            celebration_slide = os.path.join(self.config.TMP_DIR, "celebration_slide.png")
            if os.path.exists(celebration_slide):
                slides.append(celebration_slide)
            
            return slides
            
        except Exception as e:
            self.log(f"スライド作成エラー: {e}")
            return []
    
    def _extract_steps_from_explanation(self, explanation):
        """解説からステップを抽出"""
        steps = []
        lines = explanation.split('\n')
        for line in lines:
            if any(keyword in line for keyword in ['ステップ', 'Step', '手順', '①', '②', '③', '④', '⑤']):
                steps.append(line.strip())
        
        if not steps:
            # デフォルトステップ
            steps = [
                "問題を確認しよう",
                "解法を考えよう", 
                "計算を実行しよう",
                "答えを確認しよう",
                "まとめよう"
            ]
        
        return steps[:5]  # 最大5ステップ
    
    def _is_math_problem(self, explanation):
        """数学問題かどうか判定"""
        math_keywords = ['方程式', '関数', 'グラフ', 'x²', 'x^2', '微分', '積分', '三角関数']
        return any(keyword in explanation for keyword in math_keywords)
    
    def start_camera_monitoring(self):
        """カメラ監視開始"""
        self.camera = cv2.VideoCapture(0)
        threading.Thread(target=self.monitor_camera, daemon=True).start()
    
    def monitor_camera(self):
        """カメラ監視ループ"""
        while True:
            ret, frame = self.camera.read()
            if not ret:
                continue
            
            # 「おしえて！」認識
            if self.genshori_phase == "teaching" and self.detect_oshiete(frame):
                self.start_teaching()
            
            # 「Pkaisetu」認識
            if not self.pkaisetu_processing and self.detect_pkaisetu(frame):
                current_time = time.time()
                if current_time - self.last_pkaisetu_time > self.pkaisetu_cooldown:
                    self.last_pkaisetu_time = current_time
                    threading.Thread(target=self.handle_pkaisetu, args=(frame,), daemon=True).start()
            
            # その他コマンド認識
            for cmd, func in self.commands.items():
                if self.detect_command(frame, cmd):
                    func()
            
            time.sleep(0.1)
    
    def detect_oshiete(self, frame):
        """「おしえて！」文字認識"""
        try:
            temp_path = os.path.join(self.tmp_dir, "temp_frame.jpg")
            cv2.imwrite(temp_path, frame)
            text = self.yomitoku_model.predict(temp_path)
            return "おしえて" in text or "教えて" in text
        except:
            return False
    
    def detect_pkaisetu(self, frame):
        """「Pkaisetu」文字認識"""
        try:
            temp_path = os.path.join(self.tmp_dir, "temp_frame.jpg")
            cv2.imwrite(temp_path, frame)
            text = self.yomitoku_model.predict(temp_path)
            return "pkaisetu" in text.lower() or "ピカイセツ" in text
        except:
            return False
    
    def detect_command(self, frame, command):
        """コマンド文字認識"""
        try:
            temp_path = os.path.join(self.tmp_dir, "temp_frame.jpg")
            cv2.imwrite(temp_path, frame)
            text = self.yomitoku_model.predict(temp_path)
            return command in text.lower()
        except:
            return False
    
    def start_teaching(self):
        """授業開始"""
        self.log("授業開始！")
        self.speak("お兄ちゃん、一緒に勉強しよう！")
        
        for i, slide_path in enumerate(self.current_slides):
            if self.genshori_phase != "teaching":
                break
            
            self.send_image_to_vr(slide_path)
            explanation_part = self.get_slide_explanation(i)
            self.speak(explanation_part)
            time.sleep(3)  # 説明時間
    
    def handle_pkaisetu(self, frame):
        """Pkaisetu処理"""
        self.pkaisetu_processing = True
        self.speak("わかった！考えるからPkaisetuを消して待っててね～")
        
        try:
            # フレーム保存
            temp_path = os.path.join(self.tmp_dir, f"pkaisetu_{uuid.uuid4()}.jpg")
            cv2.imwrite(temp_path, frame)
            
            # 問題特定・解析
            problem_analysis = self.analyze_pkaisetu_problem(temp_path)
            detailed_explanation = self.generate_detailed_explanation(problem_analysis)
            
            # 音声で解説
            self.speak(detailed_explanation)
            
            # 必要に応じてスライド更新
            if "詳細解説が必要" in problem_analysis:
                detail_slide = self.create_detail_slide(detailed_explanation)
                self.send_image_to_vr(detail_slide)
            
        except Exception as e:
            self.log(f"Pkaisetu処理エラー: {e}")
            self.speak("ごめんね、うまく認識できなかったよ")
        
        finally:
            self.pkaisetu_processing = False
    
    def analyze_pkaisetu_problem(self, image_path):
        """Pkaisetu画像の問題解析"""
        prompt = """Analyze this image to identify the specific math problem near "Pkaisetu" text. 
Also check if there are any student's working steps or answers written, and evaluate their correctness.

Respond in Japanese with:
1. The identified problem
2. Student's work (if any)
3. Correctness evaluation
4. What needs detailed explanation"""
        
        return self.call_vlm("gemma-3-12b-it", prompt, image_path)
    
    def generate_detailed_explanation(self, problem_analysis):
        """詳細解説生成"""
        prompt = f"""Based on this analysis, create a detailed explanation as a younger sister character:

{problem_analysis}

Requirements:
- Use sister-like speech (妹口調)
- Call user "お兄ちゃん"
- If student's work is partially correct, praise the correct parts
- Point out where mistakes occur
- Give encouraging words
- Provide step-by-step guidance"""
        
        return self.call_llm("japanese-starling-chatv-7b", prompt)
    
    def call_vlm(self, model, prompt, image_path):
        """VLM API呼び出し"""
        try:
            with open(image_path, "rb") as img_file:
                image_data = base64.b64encode(img_file.read()).decode('utf-8')
            
            data = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                        ]
                    }
                ],
                "temperature": 0.7,
                "max_tokens": -1,
                "stream": False
            }
            
            response = requests.post(self.lmstudio_url, headers={"Content-Type": "application/json"}, json=data)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                self.log(f"VLM APIエラー: {response.status_code}")
                return ""
        except Exception as e:
            self.log(f"VLM呼び出しエラー: {e}")
            return ""
    
    def call_llm(self, model, prompt):
        """LLM API呼び出し"""
        try:
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": -1,
                "stream": False
            }
            
            response = requests.post(self.lmstudio_url, headers={"Content-Type": "application/json"}, json=data)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                self.log(f"LLM APIエラー: {response.status_code}")
                return ""
        except Exception as e:
            self.log(f"LLM呼び出しエラー: {e}")
            return ""
    
    def speak(self, text):
        """VOICEVOX音声合成"""
        try:
            # 音声クエリ生成
            response = requests.post(f"{self.voicevox_url}/audio_query", 
                                   params={"text": text, "speaker": 58})
            if response.status_code != 200:
                return
            
            audio_query = response.json()
            
            # 音声合成
            response = requests.post(f"{self.voicevox_url}/synthesis", 
                                   params={"speaker": 58}, 
                                   json=audio_query)
            if response.status_code != 200:
                return
            
            # 音声ファイル保存・再生
            audio_path = os.path.join(self.tmp_dir, f"voice_{uuid.uuid4()}.wav")
            with open(audio_path, 'wb') as f:
                f.write(response.content)
            
            # Unityに音声ファイルパス送信
            self.send_audio_to_unity(audio_path)
            
        except Exception as e:
            self.log(f"音声合成エラー: {e}")
    
    def send_image_to_vr(self, image_path):
        """VRに画像送信"""
        try:
            frame = cv2.imread(image_path)
            if frame is None:
                return
            
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            result, encoded_img = cv2.imencode('.jpg', frame, encode_param)
            if result:
                data = encoded_img.tobytes()
                self.udp_socket.sendto(data, (self.quest_ip, self.quest_port))
                self.log(f"画像送信: {image_path}")
        except Exception as e:
            self.log(f"画像送信エラー: {e}")
    
    def send_audio_to_unity(self, audio_path):
        """Unity音声ファイルパス送信"""
        try:
            message = f"AUDIO:{audio_path}"
            self.udp_socket.sendto(message.encode(), (self.quest_ip, self.quest_port + 1))
        except Exception as e:
            self.log(f"音声送信エラー: {e}")
    
    # コマンド処理メソッド
    def restart_explanation(self):
        self.log("解説リスタート")
        self.genshori_phase = "teaching"
        threading.Thread(target=self.start_teaching, daemon=True).start()
    
    def skip_current_slide(self):
        self.log("スライドスキップ")
    
    def repeat_current_slide(self):
        self.log("スライドリピート")
    
    def speed_up(self):
        self.log("再生速度アップ")
    
    def speed_down(self):
        self.log("再生速度ダウン")
    
    def stop_explanation(self):
        self.log("解説停止")
        self.genshori_phase = "waiting"
    
    def get_slide_explanation(self, slide_index):
        """スライド説明取得"""
        parts = self.current_explanation.split('\n\n')
        if slide_index < len(parts):
            return parts[slide_index]
        return "次のステップに進むよ！"
    
    def create_detail_slide(self, explanation):
        """詳細解説スライド作成（修正版）"""
        try:
            # 現在の問題を取得
            current_problem = self._get_current_problem()
            
            create_pkaisetu_slide(current_problem, explanation)
            detail_slide = os.path.join(self.config.TMP_DIR, "pkaisetu_slide.png")
            
            if os.path.exists(detail_slide):
                return detail_slide
            else:
                # フォールバック：簡単なテキストスライド
                return self._create_simple_text_slide(explanation)
                
        except Exception as e:
            self.log(f"詳細スライド作成エラー: {e}")
            return self._create_simple_text_slide(explanation)
    
    def _get_current_problem(self):
        """現在の問題文を取得"""
        if self.discord_history:
            # 最新の問題から抽出
            return "x² - 5x + 6 = 0"  # 仮の問題
        return "数学問題"
    
    def _create_simple_text_slide(self, text):
        """簡単なテキストスライドを作成"""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            
            fig, ax = plt.subplots(figsize=(16, 9))
            fig.patch.set_facecolor('#f0f8ff')
            
            # タイトル
            ax.text(0.5, 0.9, 'Pkaisetu - 詳細解説', 
                    ha='center', va='top', fontsize=32, weight='bold', 
                    color='#2c3e50', transform=ax.transAxes)
            
            # テキストを適切に分割
            lines = text.split('\n')
            y_pos = 0.8
            for line in lines[:10]:  # 最大10行
                if line.strip():
                    ax.text(0.1, y_pos, line, 
                            ha='left', va='top', fontsize=18, 
                            transform=ax.transAxes)
                    y_pos -= 0.07
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            slide_path = os.path.join(self.config.TMP_DIR, f"simple_slide_{int(time.time())}.png")
            plt.savefig(slide_path, dpi=150, bbox_inches='tight', 
                        facecolor='#f0f8ff', edgecolor='none')
            plt.close()
            
            return slide_path
            
        except Exception as e:
            self.log(f"簡単スライド作成エラー: {e}")
            return None
    
    def create_gui(self):
        """GUI管理画面作成"""
        self.gui_root = tk.Tk()
        self.gui_root.title("VR先生システム 管理画面")
        self.gui_root.geometry("800x600")
        
        # ステータス表示
        status_frame = ttk.Frame(self.gui_root)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(status_frame, text="システム状態:").pack(side=tk.LEFT)
        self.status_text = ttk.Label(status_frame, text="待機中", foreground="green")
        self.status_text.pack(side=tk.LEFT, padx=10)
        
        # ログ表示
        log_frame = ttk.Frame(self.gui_root)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(log_frame, text="システムログ:").pack(anchor=tk.W)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 制御ボタン
        button_frame = ttk.Frame(self.gui_root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="緊急停止", command=self.emergency_stop).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Pkaisetu実行", command=self.manual_pkaisetu).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="履歴再生", command=self.replay_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="ログクリア", command=self.clear_log).pack(side=tk.LEFT, padx=5)
    
    def update_gui_status(self, status):
        """GUI状態更新"""
        if self.status_text:
            self.status_text.config(text=status)
    
    def log(self, message):
        """ログ出力"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        if self.log_text:
            self.log_text.insert(tk.END, log_message + "\n")
            self.log_text.see(tk.END)
    
    def emergency_stop(self):
        """緊急停止"""
        self.genshori_phase = "waiting"
        self.pkaisetu_processing = False
        self.log("緊急停止実行")
    
    def manual_pkaisetu(self):
        """手動Pkaisetu実行"""
        if self.camera:
            ret, frame = self.camera.read()
            if ret:
                threading.Thread(target=self.handle_pkaisetu, args=(frame,), daemon=True).start()
    
    def replay_history(self):
        """履歴再生"""
        if self.discord_history:
            latest = self.discord_history[-1]
            threading.Thread(target=self.process_homework_image, args=(latest['file_path'],), daemon=True).start()
    
    def clear_log(self):
        """ログクリア"""
        if self.log_text:
            self.log_text.delete(1.0, tk.END)
    
    def run(self):
        """システム開始"""
        self.log("VR先生システム起動")
        
        # GUI起動
        self.create_gui()
        
        # カメラ監視開始
        self.start_camera_monitoring()
        
        # Discord Bot起動（別スレッド）
        discord_token = self.config.DISCORD_TOKEN
        if discord_token:
            threading.Thread(target=lambda: asyncio.run(self.bot.run(discord_token)), daemon=True).start()
        else:
            self.log("Discord Tokenが設定されていません")
        
        # GUI メインループ
        self.gui_root.mainloop()

if __name__ == "__main__":
    system = VRSenseiSystem()
    system.run()