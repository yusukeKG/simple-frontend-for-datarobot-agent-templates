# Simple Frontend for DataRobot Agent Templates

DataRobotのエージェントAIとチャット形式でやり取りできるWebアプリケーションです。Flaskバックエンドと、モダンなレスポンシブデザインのフロントエンドで構成されています。

## 機能

- 🤖 DataRobotエージェントデプロイメントとのリアルタイムチャット
- 💬 直感的なチャットインターフェース
- 🎨 レスポンシブデザイン（PC・タブレット・スマートフォン対応）
- 🔒 安全な環境変数による設定管理

## プロジェクト構成

```
datarobot-webapp/
├── src/
│   ├── backend/
│   │   ├── app.py                      # Flaskアプリケーションのエントリーポイント
│   │   ├── api/
│   │   │   └── routes.py               # APIエンドポイント定義
│   │   ├── config/
│   │   │   └── datarobot_config.py     # DataRobot設定管理
│   │   └── models/
│   │       └── agent.py                # エージェント統合ロジック
│   └── frontend/
│       ├── index.html                  # メインHTMLファイル
│       ├── css/
│       │   └── styles.css              # スタイルシート
│       └── js/
│           └── main.js                 # フロントエンドJavaScript
├── requirements.txt                     # Python依存関係
├── .env.template                        # 環境変数テンプレート
├── .env                                # 環境変数設定（gitignore対象）
├── start-app.sh                         # 起動スクリプト
└── README.md                           # このファイル
```

## ローカルでの開発セットアップ

### 前提条件

- Python 3.8以上
- DataRobotアカウントとAPIトークン
- デプロイ済みのDataRobotエージェント

### 1. 環境変数の設定

\`.env.template\`をコピーして\`.env\`ファイルを作成します：

```bash
cp .env.template .env
```

\`.env\`ファイルを編集して、以下の値を設定します：

```bash
# DataRobot APIトークン
DATAROBOT_API_TOKEN=your_api_token_here

# DataRobotエンドポイント（例: https://app.jp.datarobot.com/api/v2）
DATAROBOT_ENDPOINT=your_endpoint_here

# エージェントのデプロイメントID（task deployコマンドの出力から取得）
DATAROBOT_DEPLOYMENT_ID=your_deployment_id_here
```

### 2. 依存関係のインストール

```bash
# 仮想環境の作成（推奨）
python3 -m venv venv
source venv/bin/activate  # Windowsの場合: venv\\Scripts\\activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 3. アプリケーションの起動

#### オプション A: 起動スクリプトを使用

```bash
chmod +x start-app.sh  # 実行権限を付与（オプション）
./start-app.sh  # アプリケーションの起動
```

#### オプション B: 直接Pythonで起動

```bash
python -m src.backend.app
```

アプリケーションは \`http://localhost:8080\` で起動します。

## 使用方法

1. ブラウザで \`http://localhost:8080\` にアクセス
2. チャット画面が表示されます
3. メッセージ入力欄に質問やプロンプトを入力
4. 「送信」ボタンをクリックまたはEnterキーで送信
5. エージェントからの応答が表示されます

### 接続ステータス

画面上部に接続ステータスが表示されます：

- 🟢 **接続済み**: DataRobot設定が正しく構成されています
- 🟡 **設定が不完全です**: 環境変数の設定を確認してください
- 🔴 **接続エラー**: サーバーに接続できません

## APIエンドポイント

### POST /api/chat
エージェントにメッセージを送信します。

**リクエスト:**
```json
{
  "message": "Tell me about Generative AI"
}
```

**レスポンス:**
```json
{
  "success": true,
  "message": "Generative AI is...",
  "full_response": { ... }
}
```

### GET /api/config
現在の設定状態を取得します。

**レスポンス:**
```json
{
  "success": true,
  "has_deployment_id": true,
  "has_api_token": true,
  "has_endpoint": true
}
```

### GET /api/health
ヘルスチェックエンドポイント。

**レスポンス:**
```json
{
  "success": true,
  "status": "healthy"
}
```

## 開発

### ローカル開発モード

デバッグモードでアプリケーションを起動：

```bash
# デバッグモードで起動（コード変更時に自動再起動）
export FLASK_DEBUG=1
python -m src.backend.app

# 通常モードに戻す場合（環境変数を削除）
unset FLASK_DEBUG
python -m src.backend.app

# または、ワンライナーでデバッグモード起動（環境変数が残らない）
FLASK_DEBUG=1 python -m src.backend.app
```

**注意**: 
- `export FLASK_DEBUG=1`を実行すると、現在のターミナルセッションでは環境変数が保持されます
- 通常モードに戻すには`unset FLASK_DEBUG`で環境変数を削除してください
- デバッグモードは開発環境専用です。本番環境では使用しないでください

### コードの変更

- **バックエンド**: \`src/backend/\`配下のPythonファイルを編集
- **フロントエンド**: \`src/frontend/\`配下のHTML/CSS/JSファイルを編集
- デバッグモード時は、バックエンドのコード変更で自動的にサーバーが再起動します
- フロントエンドの変更は、ブラウザをリロードして確認してください

## デプロイ

**重要**: 本番環境では必ずGunicornまたはDockerを使用してください。`python -m src.backend.app`での直接起動は開発専用です。

### Dockerを使用したデプロイ（推奨）

```bash
# Dockerイメージのビルド
docker build -t datarobot-webapp .

# コンテナの起動
docker run -p 8080:8080 --env-file .env datarobot-webapp
```

### Gunicornを使用した本番環境デプロイ

```bash
# 本番環境での起動
gunicorn --bind 0.0.0.0:8080 --workers 4 src.backend.app:app

# ワーカー数の推奨値: (CPUコア数 × 2) + 1
# 例: 4コアの場合
gunicorn --bind 0.0.0.0:8080 --workers 9 src.backend.app:app
```

## トラブルシューティング

### エージェントが応答しない

1. \`.env\`ファイルの設定を確認
2. デプロイメントIDが正しいか確認
3. DataRobot APIトークンが有効か確認
4. ブラウザのコンソールでエラーを確認

### 接続エラー

1. DataRobotエンドポイントのURLが正しいか確認
2. ネットワーク接続を確認
3. ファイアウォール設定を確認

### タイムアウトエラー

- エージェントの処理に時間がかかる場合があります
- \`src/backend/models/agent.py\`の\`timeout\`パラメータを調整できます

## 技術スタック

### バックエンド
- Flask 3.0.0 - Webフレームワーク
- Flask-CORS 4.0.0 - CORS対応
- requests 2.31.0 - HTTP通信
- python-dotenv 1.0.0 - 環境変数管理

### フロントエンド
- HTML5
- CSS3（Flexbox、Grid、アニメーション）
- Vanilla JavaScript（ES6+）

## ライセンス

このプロジェクトはMITライセンスの下で提供されています。

## サポート

問題が発生した場合は、以下を確認してください：

1. [DataRobotドキュメント](https://docs.datarobot.com/)
2. プロジェクトのGitHubリポジトリ
3. DataRobotサポートチーム
