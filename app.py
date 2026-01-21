import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from styles import apply_custom_css
from views.sidebar import render_sidebar
from views.refining import render_refining_tool
# from views.package import render_package_tool  <-- 이후 추가

# 1. 초기화 및 쿠키 설정
cookies = EncryptedCookieManager(prefix="lostark-calc/", password="lostark-calc-serka-refining-pw")
if not cookies.ready():
    st.stop()

if 'api_key' not in st.session_state:
    st.session_state.api_key = cookies.get("api_key", "")
if 'target_eq' not in st.session_state:
    st.session_state.target_eq = "무기"
if 'target_lv' not in st.session_state:
    st.session_state.target_lv = 17

# 2. 페이지 설정 및 디자인 적용
st.set_page_config(page_title="로아 도구함", layout="wide")
apply_custom_css()

# API 키가 변경되었을 때 쿠키에 저장하는 로직 (세션 상태 감시)
if st.session_state.api_key != cookies.get("api_key"):
    cookies["api_key"] = st.session_state.api_key
    cookies.save()

# 3. 사이드바 렌더링 (데이터 받아오기)
price_info, inventory = render_sidebar()

# 4. 메인 콘텐츠 (탭 메뉴)
tab1, tab2 = st.tabs(["⚖️ 재련 최적화 계산기", "🎁 패키지 효율 계산기"])

with tab1:
    render_refining_tool(price_info, inventory)

with tab2:
    st.title("🎁 패키지 효율 계산기")
    # render_package_tool(price_info) <-- 패키지 뷰 완성 후 교체
    st.info("패키지 효율 계산기 도구를 준비 중입니다.")