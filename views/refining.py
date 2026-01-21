import streamlit as st
import pandas as pd
from data.refining_data import refining_data
from api_client import ITEM_ICONS

# 비즈니스 로직: 재련 전략 계산
def calculate_strategy(p_base, materials_per_try, special_mat_info, use_special=False):
    current_energy, attempt, prob_still_failing, expected_tries = 0.0, 0, 1.0, 0.0
    expected_mats = {k: 0.0 for k in materials_per_try.keys()}
    expected_special_mats = 0.0
    history = []
    
    while True:
        attempt += 1
        bonus = min((attempt - 1), 10) * 0.1
        p_current = min(p_base * (1 + bonus) + (p_base if use_special and current_energy < 100.0 else 0), 1.0)
        
        if current_energy >= 100.0:
            current_energy, p_current, prob_still_failing = 100.0, 1.0, 0

        prob_success_now = prob_still_failing * p_current
        expected_tries += prob_success_now * attempt
        
        for mat, amount in materials_per_try.items():
            expected_mats[mat] += prob_still_failing * amount
        
        if use_special and p_current < 1.0: 
            expected_special_mats += prob_still_failing * special_mat_info['count']
        
        history.append({
            "회차": f"{attempt}트", 
            "성공확률": f"{p_current*100:.2f}%", 
            "장기백": f"{current_energy:.2f}%", 
            "누적 성공률": f"{(1 - prob_still_failing) * 100:.2f}%"
        })
        
        if p_current >= 1.0: break
        current_energy += p_current * 46.5
        prob_still_failing *= (1 - p_current)
    
    max_mats = {k: amount * attempt for k, amount in materials_per_try.items()}
    max_special = special_mat_info['count'] * (attempt - 1) if use_special else 0
    return expected_tries, expected_mats, expected_special_mats, attempt, max_mats, max_special, history

# 비용 상세 계산 함수
def get_detailed_costs(expected_mats, expected_breath, b_name, price_info, inventory):
    orig, disc = 0, 0
    for m, amount in expected_mats.items():
        p = price_info.get(m, 0)
        orig += amount * p
        disc += max(0, amount - inventory.get(m, 0)) * p
    bp = price_info.get(b_name, 0)
    orig += expected_breath * bp
    disc += max(0, expected_breath - inventory.get(b_name, 0)) * bp
    return orig, disc

# 결과 카드 렌더링 함수
def show_card(res, title, b_name, is_best, has_extra_row, orig_avg, disc_avg, price_info, inventory):
    tries, mats, spec, m_try, m_mats, m_spec, hist = res
    orig_max, disc_max = get_detailed_costs(m_mats, m_spec, b_name, price_info, inventory)
    bg = "rgba(0, 104, 201, 0.05)" if is_best else "transparent"
    border_color = "#0068C9" if is_best else "#ddd"

    with st.container(border=True):
        st.markdown(f"<div style='background-color:{bg}; border-left: 5px solid {border_color}; padding: 10px; border-radius: 5px; margin-bottom:15px;'><h3 style='margin:0;'>{'⭐ ' if is_best else ''}{title} 전략</h3></div>", unsafe_allow_html=True)
        m_c1, m_c2 = st.columns(2)
        
        for col, label, tri, o_p, d_p in zip([m_c1, m_c2], ["평균 예상 비용", "장기백 예상 비용"], [f"{tries:.1f}회", f"최대 {m_try}회"], [orig_avg, orig_max], [disc_avg, disc_max]):
            with col:
                st.markdown(f"""
                    <div class="price-container">
                        <div class="price-label">{label} <span style="font-weight:normal; color:#888;">({tri})</span></div>
                        <div class="price-flow">
                            <span class="orig-val">{o_p:,.0f}G</span><span class="arrow">→</span><span class="sale-val">{d_p:,.0f}G</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        df_list = [{"icon": ITEM_ICONS.get(k, ""), "재료명": k, "평균 소모": res[1][k], "장기백 소모": res[4][k]} for k in res[1]]
        if res[2] > 0: df_list.append({"icon": ITEM_ICONS.get(b_name, ""), "재료명": b_name, "평균 소모": res[2], "장기백 소모": res[5]})
        st.dataframe(pd.DataFrame(df_list), width='stretch', hide_index=True, column_config={"icon": st.column_config.ImageColumn("", width="small"), "평균 소모": st.column_config.NumberColumn(format="%.1f"), "장기백 소모": st.column_config.NumberColumn(format="%d")})
        if not has_extra_row: st.markdown("<div style='height: 38px;'></div>", unsafe_allow_html=True)
        with st.expander(f"📊 {title} 회차별 상세 로그"): st.dataframe(pd.DataFrame(hist), width='stretch', hide_index=True)

# 메인 도구 렌더링 함수
def render_refining_tool(price_info, inventory):
    data = refining_data[st.session_state.target_eq][st.session_state.target_lv]
    breath_name = data["breath_info"]["name"]
    breath_count = data["breath_info"]["count"]

    st.title("⚖️ 세르카 장비 재련 최적화 계산기")
    with st.container(border=True):
        c1, c2, c3 = st.columns([1.5, 1.5, 4.5])
        with c1:
            st.selectbox("🛠️ 장비 종류", ["방어구", "무기"], index=0 if st.session_state.target_eq == "방어구" else 1, key="main_eq", on_change=lambda: st.session_state.update({"target_eq": st.session_state.main_eq}))
        with c2:
            st.selectbox("🎯 목표 단계", list(range(12, 26)), index=list(range(12, 26)).index(st.session_state.target_lv), key="main_lv", on_change=lambda: st.session_state.update({"target_lv": st.session_state.main_lv}))
        with c3:
            st.markdown("<div style='font-weight:bold; font-size:0.85rem; margin-bottom:5px;'>📦 1회 시도당 필요 재료</div>", unsafe_allow_html=True)
            mats_to_show = list(data["matrials_cost"].items()) + [(breath_name, breath_count)]
            mat_cols = st.columns(len(mats_to_show))
            for i, (m_name, m_amt) in enumerate(mats_to_show):
                with mat_cols[i]: st.markdown(f"<img src='{ITEM_ICONS.get(m_name, '')}' width='20'> **{m_amt:,}**", unsafe_allow_html=True)

    res_no = calculate_strategy(data["base_prob"], data["matrials_cost"], data["breath_info"], False)
    res_full = calculate_strategy(data["base_prob"], data["matrials_cost"], data["breath_info"], True)
    
    orig_no_avg, disc_no_avg = get_detailed_costs(res_no[1], 0, breath_name, price_info, inventory)
    orig_full_avg, disc_full_avg = get_detailed_costs(res_full[1], res_full[2], breath_name, price_info, inventory)

    col_res1, col_res2 = st.columns(2)
    with col_res1: show_card(res_no, "노숨", breath_name, disc_no_avg <= disc_full_avg, False, orig_no_avg, disc_no_avg, price_info, inventory)
    with col_res2: show_card(res_full, "풀숨", breath_name, disc_full_avg < disc_no_avg, True, orig_full_avg, disc_full_avg, price_info, inventory)

    st.divider()
    diff = abs(disc_no_avg - disc_full_avg)
    recommendation = "풀숨" if disc_full_avg < disc_no_avg else "노숨"
    st.success(f"✅ 귀속 재료를 고려했을 때 **{recommendation} 전략**이 약 **{diff:,.1f}G** 더 절약됩니다!")