# 札幌市食品営業許可施設データ専用MCPサーバー

NOTE:このレポジトリは、https://github.com/tyukei/mcp_okinawa_api を参考に作成しました。

札幌市の食品営業許可施設データに特化したModel Context Protocol (MCP) サーバーです。

## 概要
このMCPサーバーは札幌市のオープンデータから食品営業許可施設情報を取得し、以下の包括的な分析機能を提供します：

- **施設データの取得とキーワード検索**
- **区別・業種別の統計分析**
- **特定地域の詳細分析**
- **業界レポート生成支援**

## アーキテクチャ
```
┌─────────────────┐    ┌──────────────---───┐    ┌─────────────────┐
│   AI Assistant  │    │   MCP Server       │    │ Sapporo OpenData│
│    (Claude)     │◄──►│(SapporoFoodLicense)│◄──►│   Food License  │
└─────────────────┘    └─────────────────---┘    └─────────────────┘
```

## 主要機能

### 1. データ取得・検索機能
- `get_food_license_facilities`: 食品営業許可施設データの基本取得
- `search_food_facilities`: キーワードによる施設検索

### 2. 統計分析機能
- `get_ward_statistics`: 区別統計（施設数、業種分布）
- `get_business_type_statistics`: 業種別統計（地域分布、市場シェア）
- `get_ward_details`: 特定区の詳細分析

### 3. レポート生成支援
- `sapporo_food_business_analysis`: 業界分析レポート生成プロンプト

# setup
以下のコマンドを実行する

uvが必要です。

```bash
# プロジェクトのClone
git clone git@github.com:SuperMarimoBros/mcp_sapporo_api.git

# CDの変更
cd mcp_sapporo_api

# プロジェクトの初期化
uv init -p python3.11
uv venv
source .venv/bin/activate
uv sync
```

## 環境変数の設定
`.env`ファイルを作成し、札幌市食品営業許可施設データのリソースIDを設定してください：

```bash
# 札幌市食品営業許可施設一覧（2025年3月31日時点）
echo "RESOURCE_ID=66f1d2c7-c816-4750-a50c-108ac4268ed2" > .env
```

### 利用可能なデータセット
このMCPサーバーは食品営業許可施設データに特化していますが、参考として他のリソースIDも記載します：

| データセット名        | リソースID                                   | 対応状況 |
| ------------------- | -------------------------------------------- | ------- |
| **食品営業許可施設一覧**（2025年3月31日時点）  | `66f1d2c7-c816-4750-a50c-108ac4268ed2`        | ✅ 対応済み |
| 札幌市公共施設一覧    | `acb47fa6-3247-404a-9996-083083472817`        | 🔄 将来対応予定 |
| 避難場所一覧        | `15a81ff5-7805-4d1c-87d8-efc63b49c138`        | 🔄 将来対応予定 |

**注意**: 現在のMCPサーバーは食品営業許可施設データ専用です。他のデータセットを使用する場合は、サーバーの機能拡張が必要です。




## MCP クライアントの設定
設定ファイルは以下にあります：

~/Library/Application\ Support/Claude/claude_desktop_config.json

```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

設定ファイルには、以下をコピペしてください（user_name, pathは適切に変更してください）：

"<path>/mcp_sapporo_api"の部分は、mcp_sapporo_apiの絶対パスとなります。

```bash
# pwdを実行すると、現在の絶対パスが取得できる
pwd
```

```json
{
  "mcpServers": {
    "sapporo-food-license": {
      "command": "/Users/<user_name>/.local/bin/uv",
      "args": [
        "--directory",
        "<path>/mcp_sapporo_api",
        "run",
        "python",
        "main.py"
      ],
      "env": {
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

## 利用可能な機能とリソース

### 1. 基本データ取得
指定した件数の食品営業許可施設データを取得：
```
sapporo://food-license-facilities?limit=100
```

### 2. キーワード検索
施設名、業種、地域などでキーワード検索：
```python
# ツール: search_food_facilities
# 例: "中央区のラーメン店を検索"
search_food_facilities(q="中央区 ラーメン")
```

### 3. 区別統計分析
各区の施設数と業種分布を分析：
```python
# ツール: get_ward_statistics
get_ward_statistics()
```

### 4. 業種別統計分析
業種別の施設数と地域分布を分析：
```python
# ツール: get_business_type_statistics
get_business_type_statistics()
```

### 5. 特定区の詳細分析
指定した区の詳細情報を取得：
```python
# ツール: get_ward_details
get_ward_details(ward_name="中央区")
```

### 6. 業界分析レポート生成
分析レポート生成用のプロンプトを提供：
```python
# プロンプト: sapporo_food_business_analysis
# focus_area: "overall", "ward", "business_type", "trends"
sapporo_food_business_analysis(focus_area="overall")
```
