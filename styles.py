import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { width: 350px !important; }
            .mat-name { font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .price-text { text-align: right; font-weight: bold; font-size: 0.95rem; white-space: nowrap; }
            
            /* 예상 비용 UI */
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