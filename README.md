#途中でミスってセキュリティトークンプッシュして、セキュリティが反応して更新できなくなったのですが許してください


# VR先生システム - 妹AI家庭教師

妹キャラクターがVR空間で数学を教えてくれるAIシステムです。Discord経由で宿題の画像を送ると、解説スライドを作成してVRで表示・音声解説してくれます。

## 📋 機能一覧

- **宿題画像解析**: OCRで問題文を自動抽出
- **AI解説生成**: 妹口調で分かりやすい解説を自動生成
- **VRスライド表示**: Quest3で解説スライドを表示
- **音声解説**: VOICEVOXで可愛い声での解説
- **Pkaisetu機能**: 分からない部分を手書きで質問
- **Discord連携**: 画像アップロードで簡単操作

## 🔧 必要な環境

### ハードウェア
- Meta Quest 3 (VRヘッドセット)
- Windows PC (GPU推奨)
- Webカメラ (手書き認識用)

### ソフトウェア
- Python 3.8以上
- VOICEVOX
- LM Studio (ローカルLLM)
- Discord Bot

## 📦 インストール

### 1. リポジトリのクローン
```bash
git clone https://github.com/your-repo/imouto_study.git
cd imouto_study/model
```

### 2. 必要なライブラリのインストール
```bash
pip install -r requirements.txt
```

### 3. 追加ツールのインストール

#### VOICEVOX
1. [VOICEVOX公式サイト](https://voicevox.hiroshiba.jp/)からダウンロード
2. インストール後、起動して待機状態にする

#### LM Studio
1. [LM Studio公式サイト](https://lmstudio.ai/)からダウンロード
2. 以下のモデルをダウンロード:
   - `japanese-starling-chatv-7b` (日本語LLM)
   - `gemma-3-12b-it` (VLM)
   - `qwen2.5-coder-14b-instruct` (コード生成)

#### Tesseract OCR (Windows)
```bash
# Chocolateyを使用
choco install tesseract

# または公式サイトからインストール
# https://github.com/UB-Mannheim/tesseract/wiki
```

## ⚙️ 設定

### 1. 環境変数の設定
`.env.example`をコピーして`.env`を作成:

```bash
cp .env.example .env
```

`.env`ファイルを編集:
```env
# VR設定
QUEST_IP=192.168.1.100          # Quest3のIPアドレス
QUEST_PORT=12346
QUEST_AUDIO_PORT=12347

# API設定
LMSTUDIO_URL=http://localhost:1234/v1/chat/completions
VOICEVOX_URL=http://localhost:50021
VOICEVOX_SPEAKER_ID=58          # 関西弁キャラ

# Discord設定
DISCORD_TOKEN=your_bot_token_here
DISCORD_CHANNEL_ID=your_channel_id_here
```

### 2. Discord Bot の作成
1. [Discord Developer Portal](https://discord.com/developers/applications)でアプリケーション作成
2. Bot作成してトークンを取得
3. OAuth2でサーバーに招待 (権限: `Send Messages`, `Read Message History`, `Attach Files`)

### 3. Quest3の設定
1. Quest3を開発者モードに設定
2. 同一WiFiネットワークに接続
3. IPアドレスを確認して`.env`に設定

## 🚀 使用方法

### 1. システム起動

#### 各サービスの起動
```bash
# 1. VOICEVOXを起動
# GUIアプリケーションを起動

# 2. LM Studioを起動してモデルをロード
# japanese-starling-chatv-7bをロード
# サーバーモードで起動 (ポート1234)

# 3. VR先生システムを起動
python main.py
```

#### GUI管理画面
システム起動すると管理画面が表示されます:
- **システム状態**: 現在の処理状況
- **ログ**: リアルタイムログ表示
- **制御ボタン**: 緊急停止、手動Pkaisetu等

### 2. 宿題の提出

#### Discord経由
1. 宿題の写真を撮影
2. Discordのチャンネルに画像をアップロード
3. システムが自動で解析開始
4. 「解説準備完了」のメッセージを待つ

#### 対応ファイル形式
- 画像: `.png`, `.jpg`, `.jpeg`
- PDF: `.pdf`

### 3. VRでの学習

#### 基本操作
1. Quest3を装着
2. システムが「VR準備完了」になったら
3. 手で「**おしえて！**」と書く
4. 解説スライドと音声が開始

#### 利用可能コマンド
手書きで以下のコマンドを書けます:

| コマンド | 機能 |
|---------|------|
| `おしえて！` | 解説開始 |
| `Pkaisetu` | 詳細解説 (分からない部分を指定) |
| `restart` | 解説を最初から |
| `skip` | 次のスライドへ |
| `repeat` | 現在のスライドを繰り返し |
| `faster` | 再生速度アップ |
| `slower` | 再生速度ダウン |
| `stop` | 解説停止 |

### 4. Pkaisetu機能の使い方

#### 詳細解説の要求方法
1. 分からない問題の近くに「**Pkaisetu**」と書く
2. システムが問題を特定
3. 詳細な解説を音声とスライドで提供

#### 効果的な使い方
- 問題文の横に書く
- 間違えた計算式の近くに書く
- 理解できない部分を指す矢印と一緒に書く

## 🎯 解説の特徴

### 妹キャラクターの特徴
- **口調**: 関西弁ベースの妹キャラ
- **呼び方**: 「お兄ちゃん」
- **性格**: 優しく、励ましてくれる
- **解説スタイル**: ステップバイステップで丁寧

### 対応科目
- **数学**: 方程式、関数、微積分
- **物理**: 力学、電磁気学 (将来対応予定)
- **化学**: 化学式、計算問題 (将来対応予定)

## 🔧 トラブルシューティング

### よくある問題

#### 1. 「モデル初期化エラー」
```bash
# 解決方法
pip install easyocr pytesseract
# Tesseractの再インストール
```

#### 2. 「Discord処理エラー」
- Discord Botトークンを確認
- Bot権限を確認
- インターネット接続を確認

#### 3. 「音声合成エラー」
- VOICEVOXが起動しているか確認
- ポート50021がブロックされていないか確認

#### 4. 「VLM APIエラー」
- LM Studioが起動しているか確認
- モデルがロードされているか確認
- URLとポートを確認

#### 5. 「画像送信エラー」
- Quest3のIPアドレスを確認
- 同一ネットワークに接続されているか確認
- ファイアウォール設定を確認

### ログの確認
```bash
# システムログは管理画面で確認
# または直接ファイルで確認
tail -f ./tmp/system.log
```

### 手動テスト
```bash
# スライド生成テスト
python slide.py

# OCRテスト
python -c "from yomitoku_wrapper import YomitokuWrapper; print(YomitokuWrapper().predict('test_image.jpg'))"

# Discord接続テスト
python -c "import discord; print('Discord.py OK')"
```

## 📁 ディレクトリ構造

```
model/
├── main.py              # メインシステム
├── config.py            # 設定管理
├── slide.py             # スライド生成
├── utils.py             # ユーティリティ関数
├── yomitoku_wrapper.py  # OCRラッパー
├── nougat_wrapper.py    # PDFリーダー
├── requirements.txt     # 依存関係
├── .env.example         # 環境変数例
├── README.md           # このファイル
└── tmp/                # 一時ファイル
    ├── slides/         # 生成スライド
    ├── audio/          # 音声ファイル
    └── processing/     # 処理中ファイル
```

## 🔄 アップデート方法

```bash
# 最新版を取得
git pull origin main

# 依存関係を更新
pip install -r requirements.txt --upgrade

# 設定ファイルの更新確認
diff .env .env.example
```

## 🤝 貢献・カスタマイズ

### 新しい科目の追加
1. `slide.py`に新しいスライドテンプレートを追加
2. `main.py`の`_is_math_problem`メソッドを拡張
3. 対応する解説プロンプトを作成

### 新しいキャラクターの追加
1. `config.py`でVOICEVOXスピーカーIDを変更
2. プロンプトの口調設定を変更
3. スライドデザインをカスタマイズ

### 新しいコマンドの追加
1. `main.py`の`commands`辞書に追加
2. 対応する処理メソッドを実装
3. 手書き認識パターンを調整

## 📞 サポート

### 問題報告
- GitHub Issues で報告
- ログファイルを添付
- 再現手順を詳しく記載

### 機能要望
- GitHub Discussions で議論
- 具体的な使用例を記載

### 質問
- Discord サーバー (招待リンク)
- GitHub Discussions

## 📝 ライセンス

MIT License - 詳細は LICENSE ファイルを参照

## 🙏 謝辞

- VOICEVOX プロジェクト
- LM Studio チーム
- Meta Quest 開発チーム
- オープンソースコミュニティ

---

**注意**: このシステムは教育目的で開発されています。商用利用の場合は各サービスの利用規約を確認してください。
