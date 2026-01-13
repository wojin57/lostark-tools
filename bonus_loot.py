# 더보기 손익 계산 모듈

import math
import utils
from data.raid_data import raid_data
from api_client import price_info

def calculate_loot_cost(raid_name):
    print(f"\n{'='*25}")
    print(f"  Raid: {raid_name}")
    print(f"{'='*25}")

    # 해당 레이드의 모든 난이도를 순회 (노말, 하드 등)
    for diff_name, diff_info in raid_data[raid_name].items():
        print(f"\n[ {diff_name} - 권장 레벨: {diff_info['레벨']} ]")
        
        bonus_rewards = diff_info["보상"]["더보기"]
        total_profit = 0
        
        # 각 관문별 더보기 보상 계산
        for i, gate_reward in enumerate(bonus_rewards):
            gate_value = 0
            # 데이터에 마이너스로 기록된 골드 값을 양수(비용)로 변환
            cost = abs(gate_reward.get("골드", 0))
            
            for item_name, amount in gate_reward.items():
                if item_name == "골드":
                    continue
                
                # 시세 정보 가져오기
                price = price_info.get(item_name, 0)
                
                # 가치 계산 로직
                if "결정" in item_name:
                    # 결정류는 10개 묶음 시세이므로 10으로 나눔
                    item_value = (price / 10) * amount
                elif "파편" in item_name:
                    # 파편은 일단 가치 0으로 처리 (주머니 시세 기준 필요 시 수정)
                    item_value = 0
                else:
                    item_value = price * amount
                
                gate_value += item_value
            
            profit = gate_value - cost
            total_profit += profit
            
            status = "✅ 이득" if profit > 0 else "❌ 손해"
            print(f" > {i+1}관문: 비용 {cost:5}G | 가치 {gate_value:8,.1f}G | 결과: {profit:9,.1f}G ({status})")

        # 난이도별 최종 합계
        print(f" > {'-'*50}")
        final_status = "추천" if total_profit > 0 else "비추천"
        print(f" > {diff_name} 전체 더보기 합계: {total_profit:,.1f} 골드 이익 ({final_status})")

    print(f"\n{'='*55}\n")

while True:
    target_raid = utils.ask_question(
        message="더보기 효율을 계산할 레이드를 선택해주세요",
        choices=list(raid_data.keys()),
        default="세르카",
    )

    if target_raid is None:
        break

    calculate_loot_cost(target_raid)
    