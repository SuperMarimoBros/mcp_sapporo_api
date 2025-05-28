# 概要
札幌市オープンデータより取得できるAPIと連携するmcpサーバ

# アーキテクチャ
このMCPサーバーは札幌市のオープンデータポータル（https://ckan.pf-sapporo.jp/）からデータを取得し、Claude等のAIアシスタントから利用できるようにします。

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Assistant  │    │   MCP Server    │    │ Sapporo OpenData│
│    (Claude)     │◄──►│  (this app)     │◄──►│      API        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

# setup
以下のコマンドを実行する

```bash
# Python環境の確認と設定
pyenv versions
pyenv local 3.11.9
python --version

# プロジェクトの初期化
uv init -p python3.11
uv venv
source .venv/bin/activate
uv sync
```

## 環境変数の設定
`.env`ファイルを作成し、札幌市オープンデータのリソースIDを設定してください：

```
RESOURCE_ID=your_resource_id_here
```

## MCP クライアントの設定
設定ファイルは以下にあります：
```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

設定ファイルには、以下をコピペしてください（user_name, pathは適切に変更してください）：

```json
{
  "mcpServers": {
    "sapporo-data": {
      "command": "/Users/<user_name>/.local/bin/uv",
      "args": [
        "--directory",
        "<path>/mcp_sapporo_api",
        "run",
        "python",
        "main.py"
      ],
      "env": {
        "RESOURCE_ID": "your_resource_id_here"
      }
    }
  }
}
```

# 使用方法

## サーバーの起動
```bash
python main.py
```

## 利用可能な機能

### 1. レコード取得
指定した件数のレコードを取得：
```
sapporo://records?limit=10
```

### 2. キーワード検索
指定したキーワードでレコードを検索する`search_records`ツールを利用できます。

# データソース
- 札幌市オープンデータポータル: https://ckan.pf-sapporo.jp/
- CKAN API: https://ckan.pf-sapporo.jp/api/3/action

# ライセンス
このプロジェクトはMITライセンスの下で提供されます。
