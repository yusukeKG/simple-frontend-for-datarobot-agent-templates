# Simple Frontend for DataRobot Agent Templates

DataRobot Agent TemplatesでDataRobotにデプロイしたエージェントとチャット形式でやり取りできる簡易的なWebアプリケーションです。Flaskバックエンドと、モダンなレスポンシブデザインのフロントエンドで構成されています。

[DataRobot Agent Templates]
- https://github.com/datarobot-community/datarobot-agent-templates
- ver.11.4.0まで動作検証済み


## 機能

- 🤖 DataRobotエージェントデプロイメントとのリアルタイムチャット
- 💬 直感的なチャットインターフェース
- 🎨 レスポンシブデザイン（PC・タブレット・スマートフォン対応）
- 🔒 安全な環境変数による設定管理

## プロジェクト構成

```
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
├── requirements.txt                    # Python依存関係
├── .env.template                       # 環境変数テンプレート
├── .env                                # 環境変数設定（ローカル開発用、gitignore対象）
├── start-app.sh                        # 起動スクリプト
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

# エージェントのデプロイメントID（DataRobotのUI、URL、もしくはtask deployコマンドの出力から取得可能）
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

#### オプション A: 起動スクリプトを使用（推奨）

```bash
chmod +x start-app.sh  # 実行権限を付与（初回のみ）
./start-app.sh  # アプリケーションの起動
```

**注意**:
- ローカル開発環境では、自動的にFlask開発サーバーが起動します。
- なお、本番環境では `/opt/code` ディレクトリ配下に `start-app.sh` を配置することで、自動的に本番用のGunicornサーバーが起動します。DataRobotのカスタムアプリケーション環境もそのような構成になっています。

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

### ローカル開発とデプロイ環境の違い

| 環境 | 起動方法 | サーバー | 用途 |
|------|---------|---------|------|
| **ローカル開発** | `./start-app.sh` | Flask開発サーバー | コード編集・デバッグ |
| **DataRobot** | `./start-app.sh` (自動) | Gunicorn | 本番運用 |

`start-app.sh`はDataRobot環境（`/opt/code`）を自動判定し、適切なサーバーで起動します。

### DataRobotカスタムアプリケーション環境へのデプロイ

1. DataRobot UIにログイン
2. **レジストリ** → **新しいアプリケーションソースを追加** を選択
3. アプリケーション名を任意に入力（例: "DataRobot Simple Agent Chat"）
4. プロジェクトファイル一式をアップロード
   - **注意**: `.env` はアップロードしないでください
5. ランタイムパラメーターを設定：
   - `DATAROBT_DEPLOYMENT_ID`: 使用するエージェントのデプロイメントID
   - `DATAROBT_API_TOKEN`: 自分のDataRobot APIトークン
   - `DATAROBT_ENDPOINT`: DataRobotエンドポイントURL（デフォルト: `https://app.jp.datarobot.com/api/v2`）
6. **Deploy** をクリック

デプロイが完了すると、DataRobotが提供するURLでアプリケーションにアクセスできます。

**重要**: 
- DataRobot環境では、ランタイムパラメーターが自動的に`MLOPS_RUNTIME_PARAM_*`環境変数として注入されます
- アプリケーションは自動的にこれらを読み取り、ローカル開発用の`DATAROBOT_*`環境変数も引き続きサポートします

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
