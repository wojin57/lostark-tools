import streamlit as st
import pandas as pd
from data.refining_data import refining_data
from api_client import fetch_all_prices, ITEM_ICONS
from streamlit_cookies_manager import EncryptedCookieManager


# 1. 쿠키 매니저 초기화
cookies = EncryptedCookieManager(prefix="lostark-calc/", password="lostark-calc-serka-refining-pw")

if not cookies.ready():
    st.stop()

# 2. 세션 초기화
if 'api_key' not in st.session_state:
    st.session_state.api_key = cookies.get("api_key", "")
if 'target_eq' not in st.session_state:
    st.session_state.target_eq = "무기"
if 'target_lv' not in st.session_state:
    st.session_state.target_lv = 17

def save_to_cookie(key, value):
    cookies[key] = str(value)
    cookies.save()

# API 키 처리를 위한 콜백 함수
def process_api_key():
    # 임시 입력창에 값이 있으면 실제 변수에 저장 후 초기화
    if st.session_state.temp_key:
        st.session_state.api_key = st.session_state.temp_key
        save_to_cookie("api_key", st.session_state.api_key)
        st.session_state.temp_key = "" # 입력창 초기화

def sync_from_main():
    st.session_state.target_eq = st.session_state.main_eq
    st.session_state.target_lv = st.session_state.main_lv

# 3. 페이지 설정 및 디자인 (CSS)
st.set_page_config(page_title="로아 재련 최적화 계산기", layout="wide")
st.markdown("""
    <style>
        [data-testid="stSidebar"] { width: 350px !important; }
        [data-testid="stSidebarUserContent"] {
            padding-top: 2rem;
            padding-bottom: 2rem;
            display: block !important;
            height: auto !important;
        }
        .mat-name { font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .price-text { text-align: right; font-weight: bold; font-size: 0.95rem; white-space: nowrap; }
        
        /* 예상 비용 UI 변경: 원래 비용 -> 할인 비용 */
        .price-container {
            background-color: rgba(28, 131, 225, 0.05);
            padding: 12px;
            border-radius: 10px;
            border: 1px solid rgba(28, 131, 225, 0.1);
            margin-bottom: 10px;
            text-align: center;
        }
        .price-label { font-size: 0.85rem; color: #666; margin-bottom: 5px; font-weight: bold; }
        .price-flow { 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            gap: 10px; 
            flex-wrap: nowrap;
        }
        .orig-val { font-size: 1.1rem; color: #888; text-decoration: none; }
        .arrow { color: #0068C9; font-weight: bold; }
        .sale-val { font-size: 1.4rem; color: #E63946; font-weight: bold; }
        
        .stNumberInput label { font-size: 0.85rem !important; margin-bottom: 0px; }
    </style>
""", unsafe_allow_html=True)

# 4. 비즈니스 로직
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
            current_energy = 100.0
            p_current = 1.0
            prob_still_failing = 0

        prob_success_now = prob_still_failing * p_current
        expected_tries += prob_success_now * attempt
        
        for mat, amount in materials_per_try.items():
            expected_mats[mat] += prob_still_failing * amount
        
        if use_special and p_current < 1.0: 
            expected_special_mats += prob_still_failing * special_mat_info['count']
        
        history.append({"회차": f"{attempt}트", "성공확률": f"{p_current*100:.2f}%", "장기백": f"{current_energy:.2f}%", "누적 성공률": f"{(1 - prob_still_failing) * 100:.2f}%"})
        
        if p_current >= 1.0: break
        current_energy += p_current * 46.5
        prob_still_failing *= (1 - p_current)
    
    max_mats = {k: amount * attempt for k, amount in materials_per_try.items()}
    max_special = special_mat_info['count'] * (attempt - 1) if use_special else 0
    return expected_tries, expected_mats, expected_special_mats, attempt, max_mats, max_special, history

data = refining_data[st.session_state.target_eq][st.session_state.target_lv]
breath_name = data["breath_info"]["name"]
breath_count = data["breath_info"]["count"]

# 5. UI 상단
st.title("⚖️ 세르카 장비 재련 최적화 계산기")
with st.container(border=True):
    c1, c2, c3 = st.columns([1.5, 1.5, 4.5])
    with c1:
        st.selectbox("🛠️ 장비 종류", ["방어구", "무기"], index=0 if st.session_state.target_eq == "방어구" else 1, key="main_eq", on_change=sync_from_main)
    with c2:
        st.selectbox("🎯 목표 단계", list(range(12, 26)), index=list(range(12, 26)).index(st.session_state.target_lv), key="main_lv", on_change=sync_from_main)
    with c3:
        st.markdown("<div class='mat-summary-label'>📦 1회 시도당 필요 재료</div>", unsafe_allow_html=True)
        mats_to_show = list(data["matrials_cost"].items())
        mats_to_show.append((breath_name, breath_count))
        mat_cols = st.columns(len(mats_to_show))
        for i, (m_name, m_amt) in enumerate(mats_to_show):
            with mat_cols[i]:
                st.markdown(f"<img src='{ITEM_ICONS.get(m_name, '')}' width='20'> **{m_amt:,}**", unsafe_allow_html=True)

# 6. 사이드바 (증감 단위 및 재료 고정 노출 반영)
inventory = {}
with st.sidebar:
    st.title("⚙️ 설정")
    # API 키 입력창을 접어둘 수 있는 Expander 사용
    with st.expander("🔑 API Key 설정", expanded=not st.session_state.api_key):
        st.text_input(
            "API 키를 입력하고 Enter를 누르세요",
            key="temp_key",          # 임시 세션 키
            on_change=process_api_key, # 값이 바뀌면 실행될 함수
            placeholder="여기에 키 입력 (입력 후 비워짐)",
            label_visibility="collapsed"
        )
        if st.session_state.api_key:
            st.caption("✅ API 키가 쿠키에 저장되었습니다.")

    # 실제 API 호출은 저장된 api_key를 사용
    if st.session_state.api_key:
        price_info = fetch_all_prices(st.session_state.api_key)
        st.success("✅ 실시간 시세 적용 중")
    else:
        st.warning("⚠️ API Key를 입력해주세요.")
        price_info = {k: 0.0 for k in ITEM_ICONS.keys()}

    st.subheader("💰 실시간 시세")
    for mat_name in ["운명의 파편", "운명의 파괴석 결정", "운명의 수호석 결정", "위대한 운명의 돌파석", "상급 아비도스 융화 재료", "용암의 숨결", "빙하의 숨결"]:
        if mat_name in price_info:
            sc1, sc2, sc3 = st.columns([0.8, 4.2, 3])
            with sc1: st.image(ITEM_ICONS.get(mat_name, ""), width=22)
            with sc2: st.markdown(f"<div class='mat-name'>{mat_name}</div>", unsafe_allow_html=True)
            with sc3: st.markdown(f"<div class='price-text'>{price_info[mat_name]:,.2f}</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='font-size:1rem; font-weight:bold; margin-top:20px; color:#0068C9; border-bottom:1px solid #eee;'>🎒 내 귀속 재료 보유량</div>", unsafe_allow_html=True)
    
    # 귀속재료 입력란
    fixed_mats = ["골드", "운명의 파편", "운명의 파괴석 결정", "운명의 수호석 결정", "위대한 운명의 돌파석", "상급 아비도스 융화 재료", "용암의 숨결", "빙하의 숨결"]

    for m in fixed_mats:
        # 단위 설정
        step_val = 100000 if m == "운명의 파편" else 10000 if m == "골드" else 100

        inventory[m] = st.number_input(f"{m}", min_value=0, value=0, step=step_val, key=f"inv_{m}")

# 7. 비용 계산
def get_detailed_costs(expected_mats, expected_breath, b_name):
    orig, disc = 0, 0
    for m, amount in expected_mats.items():
        p = price_info.get(m, 0)
        orig += amount * p
        disc += max(0, amount - inventory.get(m, 0)) * p
    bp = price_info.get(b_name, 0)
    orig += expected_breath * bp
    disc += max(0, expected_breath - inventory.get(b_name, 0)) * bp
    return orig, disc

res_no = calculate_strategy(data["base_prob"], data["matrials_cost"], data["breath_info"], False)
res_full = calculate_strategy(data["base_prob"], data["matrials_cost"], data["breath_info"], True)
orig_no_avg, disc_no_avg = get_detailed_costs(res_no[1], 0, breath_name)
orig_full_avg, disc_full_avg = get_detailed_costs(res_full[1], res_full[2], breath_name)

# 8. 결과 카드
def show_card(res, title, b_name, is_best, has_extra_row, orig_avg, disc_avg):
    tries, mats, spec, m_try, m_mats, m_spec, hist = res
    orig_max, disc_max = get_detailed_costs(m_mats, m_spec, b_name)
    bg = "rgba(0, 104, 201, 0.05)" if is_best else "transparent"
    border_color = "#0068C9" if is_best else "#ddd"

    with st.container(border=True):
        st.markdown(f"<div style='background-color:{bg}; border-left: 5px solid {border_color}; padding: 10px; border-radius: 5px; margin-bottom:15px;'><h3 style='margin:0;'>{'⭐ ' if is_best else ''}{title} 전략</h3></div>", unsafe_allow_html=True)
        m_c1, m_c2 = st.columns(2)
        
        # 비용 흐름 UI 적용 (원래 비용 -> 할인 비용)
        for col, label, tri, o_p, d_p in zip([m_c1, m_c2], ["평균 예상 비용", "장기백 예상 비용"], [f"{tries:.1f}회", f"최대 {m_try}회"], [orig_avg, orig_max], [disc_avg, disc_max]):
            with col:
                st.markdown(f"""
                    <div class="price-container">
                        <div class="price-label">{label} <span style="font-weight:normal; color:#888;">({tri})</span></div>
                        <div class="price-flow">
                            <span class="orig-val">{o_p:,.0f}G</span>
                            <span class="arrow">→</span>
                            <span class="sale-val">{d_p:,.0f}G</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        df_list = [{"icon": ITEM_ICONS.get(k, ""), "재료명": k, "평균 소모": res[1][k], "장기백 소모": res[4][k]} for k in res[1]]
        if res[2] > 0: df_list.append({"icon": ITEM_ICONS.get(b_name, ""), "재료명": b_name, "평균 소모": res[2], "장기백 소모": res[5]})
        
        st.dataframe(pd.DataFrame(df_list), width='stretch', hide_index=True, column_config={"icon": st.column_config.ImageColumn("", width="small"), "평균 소모": st.column_config.NumberColumn(format="%.1f"), "장기백 소모": st.column_config.NumberColumn(format="%d")})
        if not has_extra_row: st.markdown("<div style='height: 38px;'></div>", unsafe_allow_html=True)
        with st.expander(f"📊 {title} 회차별 상세 로그 보기"): st.dataframe(pd.DataFrame(hist), width='stretch', hide_index=True)

col_res1, col_res2 = st.columns(2)
with col_res1: show_card(res_no, "노숨", breath_name, disc_no_avg <= disc_full_avg, False, orig_no_avg, disc_no_avg)
with col_res2: show_card(res_full, "풀숨", breath_name, disc_full_avg < disc_no_avg, True, orig_full_avg, disc_full_avg)

st.divider()
diff = abs(disc_no_avg - disc_full_avg)
recommendation = "풀숨" if disc_full_avg < disc_no_avg else "노숨"
st.success(f"✅ 귀속 재료를 고려했을 때 **{recommendation} 전략**이 약 **{diff:,.1f}G** 더 절약됩니다!")
