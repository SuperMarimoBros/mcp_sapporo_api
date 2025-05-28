"""
札幌市食品営業許可施設データ専用MCPサーバー

Sapporo City Food Business License Facility Data MCP Server

このMCPサーバーは札幌市のオープンデータから食品営業許可施設情報を取得し、
以下の機能を提供します：

- 施設データの取得とキーワード検索
- 区別・業種別の統計分析
- 特定地域の詳細分析
- 業界レポート生成支援

Available functions for AI agents:
- get_food_license_facilities: Get food facility data
- search_food_facilities: Search facilities by keyword  
- g# --- エントリーポイント: 札幌市食品業界データMCPサーバー起動 ---  
if __name__ == "__main__":
    mcp.run()ward_statistics: Get statistics by ward
- get_business_type_statistics: Get statistics by business type
- get_ward_details: Get detailed info for specific ward
- sapporo_food_business_analysis: Generate analysis prompts
"""

from mcp.server.fastmcp import FastMCP
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

# CKAN API のベース URL（札幌市オープンデータポータル）
CKAN_BASE   = "https://ckan.pf-sapporo.jp/api/3/action"
# 札幌市食品営業許可施設一覧のリソース ID
RESOURCE_ID = os.getenv("RESOURCE_ID")  # 66f1d2c7-c816-4750-a50c-108ac4268ed2

# FastMCP サーバインスタンスを生成
mcp = FastMCP("SapporoFoodLicense")  

# --- 1) Resource: 札幌市食品営業許可施設データの取得 ---  
@mcp.resource("sapporo://food-license-facilities?limit={limit}")
async def get_food_license_facilities(limit: int = 10) -> dict:
    """
    札幌市の食品営業許可施設一覧データを取得します。
    
    This function retrieves food business license facility data from Sapporo City's open data API.
    Use this to get information about restaurants, food stores, and other food businesses in Sapporo.
    
    Available data includes:
    - Facility name (屋号)
    - Business type (業種区分名) 
    - Location/Address (施設所在地)
    - Ward (区名)
    - License number (許可番号)
    - License date (許可年月日)
    - Applicant name (申請者名)

    Args:
        limit (int): Number of records to retrieve. Default is 10, maximum recommended is 1000.

    Returns:
        dict: JSON response containing facility data with structure:
            - success: boolean indicating API call success
            - result: dict containing records array and metadata
    """
    params = {"resource_id": RESOURCE_ID, "limit": limit}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{CKAN_BASE}/datastore_search", params=params)
        resp.raise_for_status()
        return resp.json()

# --- エンドポイント②: 食品営業許可施設のキーワード検索 ---  
@mcp.tool()
async def search_food_facilities(q: str) -> dict:
    """
    札幌市の食品営業許可施設をキーワードで検索します。
    
    Search for food business license facilities in Sapporo City by keyword.
    You can search by facility name, business type, location, or any text in the data.
    
    Useful search examples:
    - Business types: "スナック", "軽飲食", "食堂", "菓子製造"
    - Locations: "中央区", "すすきの", "大通"
    - Facility names: specific restaurant or store names
    
    Args:
        q (str): Search keyword. Can be Japanese or English text to search across all fields.
               Examples: "中央区", "スナック", "コンビニ", "ラーメン"

    Returns:
        dict: JSON response containing matching facilities with same structure as get_food_license_facilities.
              Results are ranked by relevance to the search term.
    """
    params = {"resource_id": RESOURCE_ID, "q": q}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{CKAN_BASE}/datastore_search", params=params)
        resp.raise_for_status()
        return resp.json()

# --- エンドポイント③: 区別の施設統計を取得 ---
@mcp.tool()
async def get_ward_statistics() -> dict:
    """
    札幌市の各区における食品営業許可施設の統計情報を取得します。
    
    Get statistical information about food business facilities by ward in Sapporo City.
    This provides aggregated data showing distribution across different wards.
    
    Returns comprehensive statistics including:
    - Total facilities per ward (区別総施設数)
    - Top business types per ward (区別主要業種)
    - Facility density and distribution patterns
    
    Returns:
        dict: Statistics organized by ward with facility counts and business type breakdowns.
              Useful for understanding geographic distribution of food businesses.
    """
    # 大量データを取得して集計
    params = {"resource_id": RESOURCE_ID, "limit": 5000}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{CKAN_BASE}/datastore_search", params=params)
        resp.raise_for_status()
        data = resp.json()
        
        if not data['success']:
            return data
            
        # 区別統計を計算
        records = data['result']['records']
        ward_stats = {}
        
        for record in records:
            ward = record.get('区名', 'Unknown')
            business_type = record.get('業種区分名', 'Unknown')
            
            if ward not in ward_stats:
                ward_stats[ward] = {
                    'total_facilities': 0,
                    'business_types': {}
                }
            
            ward_stats[ward]['total_facilities'] += 1
            
            if business_type not in ward_stats[ward]['business_types']:
                ward_stats[ward]['business_types'][business_type] = 0
            ward_stats[ward]['business_types'][business_type] += 1
        
        # ソートと整理
        for ward in ward_stats:
            ward_stats[ward]['business_types'] = dict(
                sorted(ward_stats[ward]['business_types'].items(), 
                       key=lambda x: x[1], reverse=True)
            )
        
        return {
            'success': True,
            'result': {
                'total_records_analyzed': len(records),
                'ward_statistics': ward_stats,
                'summary': {
                    'total_wards': len(ward_stats),
                    'most_facilities_ward': max(ward_stats.items(), key=lambda x: x[1]['total_facilities'])[0],
                    'total_facilities': sum(w['total_facilities'] for w in ward_stats.values())
                }
            }
        }

# --- エンドポイント④: 業種別統計を取得 ---
@mcp.tool()
async def get_business_type_statistics(limit: int = 5000) -> dict:
    """
    札幌市の食品営業許可施設の業種別統計情報を取得します。
    
    Get statistical information about food business facilities by business type in Sapporo City.
    This provides insights into the most common types of food businesses.
    
    Returns detailed business type analysis including:
    - Most common business types (主要業種ランキング)
    - Geographic distribution by business type
    - Business diversity metrics

    Args:
        limit (int): Number of records to retrieve for analysis. Default is 5000, maximum recommended is 10000.
    
    Returns:
        dict: Statistics organized by business type with facility counts and geographic distribution.
              Useful for market analysis and understanding business landscape.
    """
    # 大量データを取得して集計
    params = {"resource_id": RESOURCE_ID, "limit": limit}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{CKAN_BASE}/datastore_search", params=params)
        resp.raise_for_status()
        data = resp.json()
        
        if not data['success']:
            return data
            
        # 業種別統計を計算
        records = data['result']['records']
        business_stats = {}
        
        for record in records:
            business_type = record.get('業種区分名', 'Unknown')
            ward = record.get('区名', 'Unknown')
            
            if business_type not in business_stats:
                business_stats[business_type] = {
                    'total_facilities': 0,
                    'ward_distribution': {}
                }
            
            business_stats[business_type]['total_facilities'] += 1
            
            if ward not in business_stats[business_type]['ward_distribution']:
                business_stats[business_type]['ward_distribution'][ward] = 0
            business_stats[business_type]['ward_distribution'][ward] += 1
        
        # ソートと整理
        sorted_business_stats = dict(
            sorted(business_stats.items(), 
                   key=lambda x: x[1]['total_facilities'], reverse=True)
        )
        
        return {
            'success': True,
            'result': {
                'total_records_analyzed': len(records),
                'business_type_statistics': sorted_business_stats,
                'summary': {
                    'total_business_types': len(business_stats),
                    'most_common_business': max(business_stats.items(), key=lambda x: x[1]['total_facilities'])[0],
                    'total_facilities': sum(b['total_facilities'] for b in business_stats.values())
                }
            }
        }

# --- エンドポイント⑤: 特定の区の詳細情報を取得 ---
@mcp.tool()
async def get_ward_details(ward_name: str, limit: int = 1000) -> dict:
    """
    指定した区の食品営業許可施設の詳細情報を取得します。
    
    Get detailed information about food business facilities in a specific ward of Sapporo City.
    
    Args:
        ward_name (str): Name of the ward to analyze. 
                        Valid wards: "中央区", "北区", "東区", "白石区", "豊平区", "南区", "西区", "厚別区", "手稲区", "清田区"
        limit (int): Number of records to retrieve. Default is 1000, maximum recommended is 5000.
    
    Returns:
        dict: Detailed analysis of the specified ward including:
              - Total facilities in the ward
              - Business type breakdown
              - Recent licensing trends
              - Facility listings
    """
    params = {"resource_id": RESOURCE_ID, "q": ward_name, "limit": limit}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{CKAN_BASE}/datastore_search", params=params)
        resp.raise_for_status()
        data = resp.json()
        
        if not data['success']:
            return data
            
        records = data['result']['records']
        # 指定された区のレコードをフィルタリング
        ward_records = [r for r in records if r.get('区名') == ward_name]
        
        if not ward_records:
            return {
                'success': True,
                'result': {
                    'ward_name': ward_name,
                    'message': f'No facilities found for ward: {ward_name}',
                    'total_facilities': 0
                }
            }
        
        # 業種別集計
        business_types = {}
        for record in ward_records:
            business_type = record.get('業種区分名', 'Unknown')
            if business_type not in business_types:
                business_types[business_type] = 0
            business_types[business_type] += 1
        
        return {
            'success': True,
            'result': {
                'ward_name': ward_name,
                'total_facilities': len(ward_records),
                'business_type_breakdown': dict(sorted(business_types.items(), key=lambda x: x[1], reverse=True)),
                'sample_facilities': ward_records[:10],  # 最初の10件をサンプルとして返す
                'analysis_summary': f'{ward_name}には{len(ward_records)}件の食品営業許可施設があり、最も多い業種は{max(business_types.items(), key=lambda x: x[1])[0]}です。'
            }
        }

# --- プロンプト: 札幌の食品業界レポート生成 ---  
@mcp.prompt(name="sapporo_food_business_analysis", description="札幌市の食品営業許可施設データを基にした業界分析レポートを生成します。")
def sapporo_food_business_analysis(focus_area: str = "overall") -> str:
    """
    札幌市の食品業界に関する分析レポートを生成します。
    
    Generate analytical reports about Sapporo's food business landscape based on licensing data.
    
    Args:
        focus_area (str): Analysis focus - "overall", "ward", "business_type", or "trends"
    
    Returns:
        str: Prompt for generating comprehensive food business analysis
    """
    prompts = {
        "overall": """札幌市の食品営業許可施設データを分析して、以下の観点から包括的なレポートを作成してください：

1. 地域分布の特徴（区別の施設数と特色）
2. 業種構成の分析（主要業種とその特徴）
3. 市場の競争状況と機会
4. 食文化と地域特性の関係
5. ビジネス展開への示唆

データに基づいた客観的な分析と、実用的な洞察を提供してください。""",
        
        "ward": """札幌市の各区における食品営業許可施設の分布を分析し、以下について詳しく説明してください：

1. 各区の特徴的な業種構成
2. 中央区への集中とその理由
3. 住宅地域での食品業界の特色
4. 区ごとの市場機会と課題
5. 地域密着型ビジネスの可能性

地域の特性を踏まえた実践的な分析をお願いします。""",
        
        "business_type": """札幌市の食品業界における業種別の分析を行い、以下の点を詳述してください：

1. 主要業種（軽飲食、スナック等）の市場状況
2. 業種別の地域展開パターン
3. 成長業種と衰退業種の傾向
4. 新規参入機会のある業種
5. 札幌の食文化を反映した特殊な業種

市場データに基づいた戦略的な視点での分析を求めます。""",
        
        "trends": """札幌市の食品営業許可データの時系列変化を分析し、以下について考察してください：

1. 近年の許可件数の推移とその背景
2. COVID-19の影響と回復状況
3. 新しい食文化・業態の出現
4. 今後のトレンド予測
5. 持続可能な食品業界への示唆

データから読み取れるトレンドと将来展望を具体的に示してください。"""
    }
    
    return prompts.get(focus_area, prompts["overall"])

# --- エントリポイント: SSE トランスポートでサーバ起動 ---  
if __name__ == "__main__":
    mcp.run()
