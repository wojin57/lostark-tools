import streamlit as st
from api_client import fetch_all_prices, ITEM_ICONS

def render_sidebar():
    inventory = {}
    
    with st.sidebar:
        st.title("⚙️ 설정")
        
        # 1. API Key 설정 (Expandable)
        with st.expander("🔑 API Key 설정", expanded=not st.session_state.api_key):
            temp_key = st.text_input(
                "API 키 입력", 
                key="temp_key_input",
                placeholder="키 입력 후 Enter",
                label_visibility="collapsed"
            )
            # API 키 처리 로직
            if temp_key:
                st.session_state.api_key = temp_key
                # 쿠키 저장은 app.py에서 전달받은 함수나 직접 세션 관리를 통해 처리
                st.rerun()

        # 2. 실시간 시세 정보
        if st.session_state.api_key:
            price_info = fetch_all_prices(st.session_state.api_key)
            st.success("✅ 실시간 시세 적용 중")
        else:
            st.warning("⚠️ API Key를 입력해주세요.")
            price_info = {k: 0.0 for k in ITEM_ICONS.keys()}

        st.subheader("💰 실시간 시세")
        target_mats = [
            "운명의 파편", "운명의 파괴석 결정", "운명의 수호석 결정", 
            "위대한 운명의 돌파석", "상급 아비도스 융화 재료", "용암의 숨결", "빙하의 숨결"
        ]
        
        for mat_name in target_mats:
            if mat_name in price_info:
                sc1, sc2, sc3 = st.columns([0.8, 4.2, 3])
                with sc1: st.image(ITEM_ICONS.get(mat_name, ""), width=22)
                with sc2: st.markdown(f"<div class='mat-name'>{mat_name}</div>", unsafe_allow_html=True)
                with sc3: st.markdown(f"<div class='price-text'>{price_info[mat_name]:,.2f}</div>", unsafe_allow_html=True)
        
        # 3. 귀속 재료 보유량 입력
        st.markdown("<div style='font-size:1rem; font-weight:bold; margin-top:20px; color:#0068C9; border-bottom:1px solid #eee;'>🎒 내 귀속 재료 보유량</div>", unsafe_allow_html=True)
        
        fixed_mats = ["골드", "운명의 파편", "운명의 파괴석 결정", "운명의 수호석 결정", "위대한 운명의 돌파석", "상급 아비도스 융화 재료", "용암의 숨결", "빙하의 숨결"]

        for m in fixed_mats:
            step_val = 100000 if m == "운명의 파편" else 10000 if m == "골드" else 100
            inventory[m] = st.number_input(f"{m}", min_value=0, value=0, step=step_val, key=f"inv_{m}")

    return price_info, inventory