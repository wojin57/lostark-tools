import requests
import streamlit as st

ITEM_ICONS = {
    "운명의 파편": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_12_92.png",
    "운명의 파괴석 결정": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_13_249.png",
    "운명의 수호석 결정": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_13_250.png",
    "위대한 운명의 돌파석": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_13_251.png",
    "상급 아비도스 융화 재료": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_13_252.png",
    "용암의 숨결": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_12_171.png",
    "빙하의 숨결": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_12_172.png",
    "골드": "https://cdn-lostark.game.onstove.com/efui_iconatlas/money/money_4.png"
}

@st.cache_data(ttl=600) # 10분간 캐싱하여 API 호출 횟수 절약
def fetch_all_prices(api_key):
    if not api_key:
        return {k: 0.0 for k in ITEM_ICONS.keys()}

    url = "https://developer-lostark.game.onstove.com/markets/items"
    headers = {
        "accept": "application/json",
        "authorization": f"bearer {api_key}",
        "Content-Type": "application/json",
    }

    target_items = {
        "운명의 파편 주머니(소)": {"CategoryCode": 50010, "ItemId": 66130141},
        "운명의 파편 주머니(중)": {"CategoryCode": 50010, "ItemId": 66130142},
        "운명의 파편 주머니(대)": {"CategoryCode": 50010, "ItemId": 66130143},
        "운명의 파괴석": {"CategoryCode": 50010, "ItemId": 66102006},
        "운명의 파괴석 결정": {"CategoryCode": 50010, "ItemId": 66102007},
        "운명의 수호석": {"CategoryCode": 50010, "ItemId": 66102106},
        "운명의 수호석 결정": {"CategoryCode": 50010, "ItemId": 66102107},
        "운명의 돌파석": {"CategoryCode": 50010, "ItemId": 66110225},
        "위대한 운명의 돌파석": {"CategoryCode": 50010, "ItemId": 66110226},
        "아비도스 융화 재료": {"CategoryCode": 50010, "ItemId": 6861012},
        "상급 아비도스 융화 재료": {"CategoryCode": 50010, "ItemId": 6861013},
        "용암의 숨결": {"CategoryCode": 50020, "ItemId": 66111131},
        "빙하의 숨결": {"CategoryCode": 50020, "ItemId": 66111132},
    }

    raw_prices = {}
    for item_name, info in target_items.items():
        payload = {"Sort": "GRADE", "CategoryCode": info["CategoryCode"], "ItemTier": 4, "ItemName": item_name, "PageNo": 0}
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                raw_prices[item_name] = data['Items'][0]['RecentPrice'] if data['Items'] else 0.0
            else:
                raw_prices[item_name] = 0.0
        except:
            raw_prices[item_name] = 0.0
            
    # 최종 가격 가공
    processed = {
        "운명의 파편": min(raw_prices.get("운명의 파편 주머니(소)", 0)/1000, raw_prices.get("운명의 파편 주머니(중)", 0)/2000, raw_prices.get("운명의 파편 주머니(대)", 0)/3000) if raw_prices.get("운명의 파편 주머니(소)") else 0,
        "운명의 파괴석 결정": min(raw_prices.get("운명의 파괴석", 0)*5, raw_prices.get("운명의 파괴석 결정", 0)) / 100,
        "운명의 수호석 결정": min(raw_prices.get("운명의 수호석", 0)*5, raw_prices.get("운명의 수호석 결정", 0)) / 100,
        "위대한 운명의 돌파석": min(raw_prices.get("운명의 돌파석", 0)*5, raw_prices.get("위대한 운명의 돌파석", 0)),
        "상급 아비도스 융화 재료": min(raw_prices.get("아비도스 융화 재료", 0)*5, raw_prices.get("상급 아비도스 융화 재료", 0)),
        "용암의 숨결": raw_prices.get("용암의 숨결", 0),
        "빙하의 숨결": raw_prices.get("빙하의 숨결", 0),
        "골드": 1.0
    }
    return processed

# import requests, os
# from dotenv import load_dotenv, set_key

# # .env 파일의 내용을 환경 변수로 로드
# env_path = ".env"
# load_dotenv(env_path)

# def get_api_key():
#     # 1. 시스템 환경 변수 또는 .env 확인
#     key = os.getenv("API_KEY")

#     # 2. 사용자에게 직접 입력 받기
#     if not key:
#         print("로스트아크 API KEY가 설정되어 있지 않습니다.")
#         key = input("https://developer-lostark.game.onstove.com 에서 API KEY를 발급받은 뒤 입력해주세요: ").strip()
        
#         if key:
#             set_key(env_path, "API_KEY", key)
#             os.environ["API_KEY"] = key # 환경 변수 즉시 반영
 
#     return key

# def get_market_prices():
#     API_KEY = get_api_key()

#     if not API_KEY:
#         print("API KEY가 없어 정보를 불러올 수 없습니다.")
#         return {}

#     print("시장 가격 정보를 불러오는 중...")    
#     url = "https://developer-lostark.game.onstove.com/markets/items"
#     headers = {
#         "accept": "application/json",
#         "authorization": f"bearer {API_KEY}",
#         "Content-Type": "application/json",
#     }

#     target_items = {
#         "운명의 파편 주머니(소)": {
#             "CategoryCode": 50010,
#             "ItemId": 66130141,
#         },
#         "운명의 파편 주머니(중)": {
#             "CategoryCode": 50010,
#             "ItemId": 66130142,
#         },
#         "운명의 파편 주머니(대)": {
#             "CategoryCode": 50010,
#             "ItemId": 66130143,
#         },
#         "운명의 파괴석": {
#             "CategoryCode": 50010,
#             "ItemId": 66102006,
#         },
#         "운명의 파괴석 결정": {
#             "CategoryCode": 50010,
#             "ItemId": 66102007,
#         },
#         "운명의 수호석": {
#             "CategoryCode": 50010,
#             "ItemId": 66102106,
#         },
#         "운명의 수호석 결정": {
#             "CategoryCode": 50010,
#             "ItemId": 66102107,
#         },
#         "운명의 돌파석": {
#             "CategoryCode": 50010,
#             "ItemId": 66110225,
#         },
#         "위대한 운명의 돌파석": {
#             "CategoryCode": 50010,
#             "ItemId": 66110226,
#         },
#         "아비도스 융화 재료": {
#             "CategoryCode": 50010,
#             "ItemId": 6861012,
#         },
#         "상급 아비도스 융화 재료": {
#             "CategoryCode": 50010,
#             "ItemId": 6861013,
#         },
#         "용암의 숨결": {
#             "CategoryCode": 50020,
#             "ItemId": 66111131,
#         },
#         "빙하의 숨결": {
#             "CategoryCode": 50020,
#             "ItemId": 66111132,
#         },
#     }

#     prices = {}

#     for item_name, item_info in target_items.items():
#         payload = {
#             "Sort": "GRADE",
#             "CategoryCode": item_info["CategoryCode"],
#             "CharacterClass": None,
#             "ItemTier": 4,
#             "ItemGrade": None,
#             "ItemName": item_name,
#             "PageNo": 0,
#             "SortCondition": "ASC",
#         }
#         try:
#             response = requests.post(url, headers=headers, json=payload)
#             if response.status_code == 200:
#                 data = response.json()
#                 if data:
#                     prices[item_name] = data['Items'][0]['RecentPrice']
#             else:
#                 print(f"API 호출 실패 ({item_name}): {response.status_code}")
#                 prices[item_name] = 0.0
#         except Exception as e:
#             print(f"오류 발생: {e}")
#             prices[item_name] = 0.0
            
#     return prices

# def get_price_info():
#     prices = get_market_prices()
#     price_info = {
#         "운명의 파편": min(prices["운명의 파편 주머니(소)"] / 1000, prices["운명의 파편 주머니(중)"] / 2000, prices["운명의 파편 주머니(대)"] / 3000),
#         "운명의 파괴석": prices["운명의 파괴석"] / 100,
#         "운명의 파괴석 결정": min(prices["운명의 파괴석"] * 5, prices["운명의 파괴석 결정"]) / 100,
#         "운명의 수호석": prices["운명의 수호석"] / 100,
#         "운명의 수호석 결정": min(prices["운명의 수호석"] * 5, prices["운명의 수호석 결정"]) / 100,
#         "운명의 돌파석": prices["운명의 돌파석"],
#         "위대한 운명의 돌파석": min(prices["운명의 돌파석"] * 5, prices["위대한 운명의 돌파석"]),
#         "아비도스 융화 재료": prices["아비도스 융화 재료"],
#         "상급 아비도스 융화 재료": min(prices["아비도스 융화 재료"] * 5, prices["상급 아비도스 융화 재료"]),
#         "골드": 1,
#         "용암의 숨결": prices["용암의 숨결"],
#         "빙하의 숨결": prices["빙하의 숨결"],
#     }

#     return price_info

# price_info = get_price_info()
# ITEM_ICONS = {
#     "운명의 파편": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_12_92.png",
#     "운명의 파괴석": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_12_84.png",
#     "운명의 파괴석 결정": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_13_249.png",
#     "운명의 수호석": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_12_89.png",
#     "운명의 수호석 결정": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_13_250.png",
#     "운명의 돌파석": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_12_85.png",
#     "위대한 운명의 돌파석": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_13_251.png",
#     "아비도스 융화 재료": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_12_86.png",
#     "상급 아비도스 융화 재료": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_13_252.png",
#     "용암의 숨결": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_12_171.png",
#     "빙하의 숨결": "https://cdn-lostark.game.onstove.com/efui_iconatlas/use/use_12_172.png",
#     "골드": "https://cdn-lostark.game.onstove.com/efui_iconatlas/money/money_4.png"
# }