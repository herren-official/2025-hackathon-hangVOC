import streamlit as st
from datetime import datetime

def format_timestamp(ts: str) -> str:
    """Unix timestamp를 읽기 쉬운 형식으로 변환"""
    try:
        dt = datetime.fromtimestamp(float(ts))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return ts

def apply_custom_css():
    """커스텀 CSS 적용"""
    st.markdown("""
    <style>
    /* 메인 컨테이너 스타일 */
    .main {
        padding-top: 2rem;
    }
    
    /* 검색 박스 스타일 */
    .stTextArea textarea {
        font-size: 16px;
        border-radius: 10px;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        border-radius: 20px;
        font-weight: bold;
    }
    
    /* 성공 메시지 스타일 */
    .stSuccess {
        border-radius: 10px;
    }
    
    /* 정보 박스 스타일 */
    .stInfo {
        border-radius: 10px;
        background-color: #f0f8ff;
    }
    
    /* 확장 패널 스타일 */
    .streamlit-expanderHeader {
        font-weight: bold;
        font-size: 16px;
    }
    
    /* 사이드바 스타일 */
    .css-1d391kg {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

def show_loading_animation(text="처리 중..."):
    """로딩 애니메이션 표시"""
    with st.spinner(text):
        import time
        time.sleep(0.5)  # 시뮬레이션용

def truncate_text(text: str, max_length: int = 200) -> str:
    """텍스트를 지정된 길이로 자르기"""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text