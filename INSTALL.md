# VR先生システム インストールガイド

## 📋 事前準備チェックリスト

### ハードウェア要件
- [ ] Windows 10/11 PC
- [ ] Meta Quest 3
- [ ] Webカメラ
- [ ] GPU (推奨: GTX 1060以上)
- [ ] RAM 8GB以上
- [ ] ストレージ 10GB以上の空き容量

### ネットワーク要件
- [ ] 安定したWiFi環境
- [ ] PCとQuest3が同一ネットワーク
- [ ] インターネット接続 (Discord, AI API用)

## 🔧 Step 1: 基本環境の構築

### Python環境のセットアップ
```bash
# Python 3.8以上がインストールされていることを確認
python --version

# pipの更新
python -m pip install --upgrade pip

# 仮想環境の作成（推奨）
python -m venv vr_sensei_env
vr_sensei_env\Scripts\activate  # Windows
```

### リポジトリのクローン
```bash
git clone https://github.com/your-repo/imouto_study.git
cd imouto_study/model
```

## 🔧 Step 2: 依存関係のインストール

### 基本ライブラリ
```bash
pip install -r requirements.txt
```

### Tesseract OCR (Windows)
```bash
# Chocolateyを使用する場合
choco install tesseract

# 手動インストールの場合
# 1. https://github.com/UB-Mannheim/tesseract/wiki からダウンロード
# 2. インストール
# 3. 環境変数PATHに追加
```

### 日本語フォントの確認
```bash
# msgothic.ttcが存在するか確認
dir C:\Windows\Fonts\msgothic.ttc
```

## 🔧 Step 3: AIモデルの準備

### LM Studioのインストール
1. [LM Studio公式サイト](https://lmstudio.ai/)からダウンロード
2. インストール実行
3. 初回起動設定

### 必要モデルのダウンロード
LM Studio内で以下のモデルを検索してダウンロード:

```
japanese-starling-chatv-7b      # 日本語対話 (約4GB)
gemma-3-12b-it                  # 視覚言語モデル (約7GB)
qwen2.5-coder-14b-instruct      # コード生成 (約8GB)
```

**注意**: 合計約20GBのダウンロードが必要です。時間がかかる場合があります。

### モデルの起動テスト
```bash
# LM Studioでサーバーモードを開始
# 1. Chat タブで japanese-starling-chatv-7b を選択
# 2. Server タブに移動
# 3. "Start Server" をクリック
# 4. http://localhost:1234 でサーバーが起動することを確認
```

## 🔧 Step 4: VOICEVOX の設定

### インストール
1. [VOICEVOX公式サイト](https://voicevox.hiroshiba.jp/)からダウンロード
2. インストール実行
3. 初回起動で音声ライブラリをダウンロード

### 音声テスト
```bash
# VOICEVOXを起動
# 1. アプリケーションを起動
# 2. 「こんにちは」と入力して音声生成テスト
# 3. 正常に音声が再生されることを確認
```

### API サーバーモード
```bash
# VOICEVOXをAPIモードで起動
# コマンドラインから実行:
"C:\Program Files\VOICEVOX\VOICEVOX.exe" --enable_api
```

## 🔧 Step 5: Discord Bot の作成

### Discord Developer Portal での設定
1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセス
2. "New Application" をクリック
3. アプリケーション名を入力 (例: "VR先生")

### Bot の作成
1. 左メニューから "Bot" を選択
2. "Add Bot" をクリック
3. Token をコピー（後で.envファイルに使用）

### 権限の設定
1. 左メニューから "OAuth2" > "URL Generator" を選択
2. Scopes: `bot` を選択
3. Bot Permissions: 以下を選択
   - Send Messages
   - Read Message History
   - Attach Files
   - Use Slash Commands
4. 生成されたURLでサーバーに招待

## 🔧 Step 6: Quest 3 の設定

### 開発者モードの有効化
1. Meta Quest Developer Hub をインストール
2. Meta アカウントで開発者登録
3. Quest 3 を開発者モードに設定

### ネットワーク設定
```bash
# Quest 3 のIPアドレスを確認
# Settings > Wi-Fi > Advanced > IP Address
```

### Unity アプリの準備
```bash
# Unity プロジェクトをビルド
# または提供されたAPKをインストール
# adb install VRSensei.apk
```

## 🔧 Step 7: 環境設定ファイル

### .env ファイルの作成
```bash
cp .env.example .env
```

### .env ファイルの編集
```env
# VR設定
QUEST_IP=192.168.1.100          # Quest3のIPアドレスに変更
QUEST_PORT=12346
QUEST_AUDIO_PORT=12347

# API設定
LMSTUDIO_URL=http://localhost:1234/v1/chat/completions
VOICEVOX_URL=http://localhost:50021
VOICEVOX_SPEAKER_ID=58

# Discord設定
DISCORD_TOKEN=your_bot_token_here    # 実際のトークンに変更
DISCORD_CHANNEL_ID=your_channel_id   # チャンネルIDに変更
```

## 🔧 Step 8: 動作テスト

### 個別コンポーネントのテスト

#### 1. OCRテスト
```bash
python -c "
from yomitoku_wrapper import YomitokuWrapper
ocr = YomitokuWrapper()
print('OCR初期化:', 'OK' if ocr else 'NG')
"
```

#### 2. LLM APIテスト
```bash
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "japanese-starling-chatv-7b",
    "messages": [{"role": "user", "content": "こんにちは"}]
  }'
```

#### 3. VOICEVOX APIテスト
```bash
curl -X POST "http://localhost:50021/audio_query?text=こんにちは&speaker=58"
```

#### 4. スライド生成テスト
```bash
python slide.py
# ./tmp/slide_0.png が生成されることを確認
```

### 統合テスト
```bash
python main.py
```

#### 確認項目
- [ ] GUI管理画面が表示される
- [ ] "モデル初期化完了" のログが表示される
- [ ] Discord Bot準備完了のログが表示される
- [ ] エラーログが出ていない

## 🔧 Step 9: 初回利用テスト

### テスト用画像の準備
```bash
# 数学問題の写真を撮影
# または ./test_images/sample_math.jpg を使用
```

### Discord経由でのテスト
1. Discord チャンネルに画像をアップロード
2. 管理画面で「画像解析中...」→「VR準備完了」の流れを確認
3. Quest 3 で「おしえて！」と手書き
4. スライド表示と音声再生を確認

## 🚨 トラブルシューティング

### よくあるエラーと解決方法

#### ModuleNotFoundError
```bash
# 解決方法
pip install -r requirements.txt
# 仮想環境がアクティブになっているか確認
```

#### "LLM APIエラー"
```bash
# LM Studioの確認
# 1. japanese-starling-chatv-7b がロードされているか
# 2. Server が起動しているか (緑色のランプ)
# 3. ポート1234が使用可能か
```

#### "音声合成エラー"
```bash
# VOICEVOXの確認
# 1. アプリケーションが起動しているか
# 2. APIサーバーモードになっているか
# 3. ポート50021が使用可能か
```

#### "Quest接続エラー"
```bash
# ネットワークの確認
ping 192.168.1.100  # Quest3のIP
# ファイアウォールの確認
```

### ログの確認方法
```bash
# システムログ
tail -f ./tmp/system.log

# 詳細デバッグ
python main.py --debug
```

## 📞 サポート

### 問題が解決しない場合
1. ログファイルを確認
2. 設定ファイルを再確認
3. GitHub Issues で報告
4. 必要な情報:
   - OS バージョン
   - Python バージョン
   - エラーメッセージ
   - ログファイル

### 成功確認チェックリスト
- [ ] すべてのモジュールが正常に初期化
- [ ] Discord Bot が応答
- [ ] VR でスライド表示
- [ ] 音声が正常に再生
- [ ] Pkaisetu 機能が動作

インストール完了後は [README.md](README.md) を参照して使用方法を確認してください。
