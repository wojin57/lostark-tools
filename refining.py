import math
import utils
from data.refining_data import refining_data
from api_client import price_info

def get_display_width(text):
    width = 0
    for char in text:
        # 한글 음절 및 자모 범위 체크
        if '\uAC00' <= char <= '\uD7A3' or '\u1100' <= char <= '\u11FF':
            width += 2
        else:
            width += 1
    return width

def pad_korean(text, total_width, align='left'):
    current_width = get_display_width(text)
    padding = total_width - current_width
    if padding < 0: padding = 0
    
    if align == 'left':
        return text + ' ' * padding
    elif align == 'right':
        return ' ' * padding + text
    else: # center
        left_pad = padding // 2
        right_pad = padding - left_pad
        return ' ' * left_pad + text + ' ' * right_pad

def calculate_refining_strategy(p_base, materials_per_try, special_mat_info, use_special=False):
    current_energy = 0.0
    expected_tries = 0.0
    attempt = 0
    prob_still_failing = 1.0  
    
    expected_mats = {k: 0.0 for k in materials_per_try.keys()}
    expected_special_mats = 0.0

    strategy_name = "풀숨" if use_special else "노숨"
    print(f"\n[{strategy_name} 전략 상세 로그]")
    print(f"{'회차':^2} | {'성공률':^4} | {'장기':^4} | {'누적 성공률':^6}")
    print("-" * 50)

    while True:
        attempt += 1
        bonus_multiplier = min((attempt - 1), 10) * 0.1
        p_current = p_base * (1 + bonus_multiplier)
        
        if use_special and current_energy < 100.0:
            p_current += p_base
        
        if current_energy >= 100.0:
            p_current = 1.0
            
        prob_success_now = prob_still_failing * p_current
        expected_tries += prob_success_now * attempt
        
        for mat, amount in materials_per_try.items():
            expected_mats[mat] += prob_still_failing * amount
        
        if use_special and p_current < 1.0: 
            expected_special_mats += prob_still_failing * special_mat_info['count']

        current_energy_log = current_energy
        
        if p_current < 1.0:
            current_energy += p_current * 46.5
            prob_still_failing *= (1 - p_current)
        else:
            current_energy_log = 100.00
            prob_still_failing = 0.0 
            
        cumulative_success_rate = 1 - prob_still_failing
        print(f"{attempt:>4} | {p_current*100:>6.2f}% | {current_energy_log:>6.2f} | {cumulative_success_rate:>7.2%}")

        if p_current >= 1.0:
            break

    # 장기백 소모량 계산 (단순 시도 횟수 곱)
    max_mats = {k: amount * attempt for k, amount in materials_per_try.items()}
    # 특수 재료는 장기백 직전 판(성공 확정 전)까지만 넣으므로 (attempt - 1)
    max_special = special_mat_info['count'] * (attempt - 1) if use_special else 0

    return expected_tries, expected_mats, expected_special_mats, attempt, max_mats, max_special

# 결과 출력용 함수
def print_summary(res, strategy_name):
    tries, mats, special, max_attempt, max_mats, max_special = res
    padding_name = 24  # 한글 너비를 고려한 충분한 공간
    
    print(f"\n[{strategy_name} 전략 재료 소모량]")
    
    h_name = pad_korean("재료명", padding_name, 'center')
    h_avg = pad_korean("평균 소모량", 12, 'center')
    h_max = pad_korean("장기백 소모량", 14, 'center')
    
    print(f"{h_name} | {h_avg} | {h_max}")
    print("-" * 65)
    
    total_avg_cost, total_max_cost = 0.0, 0

    for mat in matarials_cost.keys():
        name_td = pad_korean(mat, padding_name, 'left')
        print(f"{name_td} | {mats[mat]:>12,.1f} | {max_mats[mat]:>10,}")
        total_avg_cost += mats[mat] * price_info.get(mat, 0)
        total_max_cost += max_mats[mat] * price_info.get(mat, 0)
        
    if special > 0 or max_special > 0:
        name_td = pad_korean(breath_info["name"], padding_name, 'left')
        print(f"{name_td} | {special:>12,.1f} | {max_special:>10,}")
        total_avg_cost += special * price_info.get(breath_info["name"], 0)
        total_max_cost += max_special * price_info.get(breath_info["name"], 0)

    print("-" * 65)
    label_td = pad_korean("재련 시도 횟수", padding_name, 'left')
    print(f"{label_td} | {tries:>9.1f} 회 | {max_attempt:>7} 회")

    name_total_cost = pad_korean("재료 골드 가치", padding_name, "left")
    print(f"{name_total_cost} | {total_avg_cost:>12,.1f} | {int(total_max_cost):>10,}")

    return total_avg_cost, total_max_cost

while True:
    target_equipment = utils.ask_question(
        message="재련할 장비를 선택해주세요",
        choices=["방어구", "무기"],
        default="무기",
    )

    if target_equipment is None:
        break
    
    target_level = int(utils.ask_question(
        message="목표 재련 단계를 선택해주세요",
        choices=[str(i) for i in range(12, 26)],
        default="17",
    ))

    if target_level is None:
        break
    
    data = refining_data[target_equipment][target_level]
    base_prob, matarials_cost, breath_info = data["base_prob"], data["matrials_cost"], data["breath_info"]

    # 데이터 계산
    res_no = calculate_refining_strategy(base_prob, matarials_cost, breath_info, use_special=False)
    res_full = calculate_refining_strategy(base_prob, matarials_cost, breath_info, use_special=True)

    # 최종 요약 출력
    print("\n" + "="*60)
    print(f"최종 결과 요약 - {target_equipment} 재련 {target_level}단계 목표")
    no_avg_cost, no_max_cost = print_summary(res_no, "노숨")
    full_avg_cost, full_max_cost = print_summary(res_full, "풀숨")

    print("\n" + "=" * 60)
    if no_avg_cost > full_avg_cost:
        savings = no_avg_cost - full_avg_cost
        print(f"▶ 풀숨 전략이 평균 {savings:,.1f}골드 절약!")
    else:
        extra = full_avg_cost - no_avg_cost
        print(f"▶ 노숨 전략이 평균 {extra:,.1f}골드 절약!")