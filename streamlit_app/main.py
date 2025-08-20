import streamlit as st
import requests
import json
from typing import Optional

# 페이지 설정
st.set_page_config(
    page_title="Slack Q&A Search",
    page_icon="🔍",
    layout="wide"
)

# API 엔드포인트 설정
API_BASE_URL = "http://localhost:8000/api/v1"

# 세션 상태 초기화
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

def search_messages(question: str, top_k: int = 10) -> Optional[dict]:
    """API를 통해 메시지 검색"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/search",
            json={"question": question, "top_k": top_k}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"검색 실패: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"API 연결 실패: {str(e)}")
        return None

def upload_slack_data(file):
    """슬랙 데이터 업로드 및 인덱싱"""
    try:
        files = {'file': (file.name, file.getvalue())}
        response = requests.post(
            f"{API_BASE_URL}/index",
            files=files
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"업로드 실패: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"업로드 실패: {str(e)}")
        return None

# 메인 UI
st.title("🔍 Slack Q&A Instant Search")
st.markdown("사내 슬랙 대화를 검색하고 빠르게 해결책을 찾아보세요!")

# 사이드바 - 데이터 업로드
with st.sidebar:
    st.header("⚙️ 설정")
    
    st.subheader("📤 슬랙 데이터 업로드")
    uploaded_file = st.file_uploader(
        "Slack export JSON 파일을 선택하세요",
        type=['json'],
        help="Slack workspace export 파일을 업로드하여 인덱싱합니다"
    )
    
    if uploaded_file is not None:
        if st.button("🚀 인덱싱 시작", type="primary"):
            with st.spinner("데이터 인덱싱 중... 잠시만 기다려주세요"):
                result = upload_slack_data(uploaded_file)
                if result:
                    st.success(f"✅ 인덱싱 완료! {result['chunk_count']}개 청크 생성됨")
                    st.balloons()
    
    st.divider()
    
    # 검색 설정
    st.subheader("🔧 검색 설정")
    top_k = st.slider(
        "검색 결과 개수",
        min_value=1,
        max_value=20,
        value=10,
        help="검색 시 참고할 메시지 개수"
    )

# 메인 컨텐츠 영역
col1, col2 = st.columns([2, 1])

with col1:
    # 검색 입력
    st.subheader("💬 무엇을 찾고 계신가요?")
    
    # 검색 폼
    with st.form(key="search_form"):
        question = st.text_area(
            "질문을 입력하세요",
            placeholder="예: Docker 컨테이너 빌드 오류 해결 방법은?",
            height=100
        )
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            search_button = st.form_submit_button("🔍 검색", type="primary", use_container_width=True)
        with col_btn2:
            clear_button = st.form_submit_button("🗑️ 초기화", use_container_width=False)
    
    if clear_button:
        st.session_state.search_history = []
        st.rerun()
    
    # 검색 실행
    if search_button and question:
        with st.spinner("검색 중..."):
            result = search_messages(question, top_k)
            
            if result:
                # 검색 기록에 추가
                st.session_state.search_history.append({
                    'question': question,
                    'answer': result['answer'],
                    'sources': result['sources']
                })
                
                # 답변 표시
                st.success("✅ 답변을 찾았습니다!")
                
                # 답변 박스
                st.markdown("### 📝 답변")
                st.info(result['answer'])
                
                # 근거 메시지 표시
                if result['sources']:
                    with st.expander("📚 참고한 슬랙 메시지 보기", expanded=False):
                        for i, source in enumerate(result['sources'], 1):
                            st.markdown(f"**메시지 {i}**")
                            st.text(source['text'])
                            if source.get('metadata'):
                                meta = source['metadata']
                                st.caption(
                                    f"메시지 수: {meta.get('message_count', 'N/A')} | "
                                    f"유사도: {1 - source.get('distance', 0):.2f}"
                                )
                            st.divider()

with col2:
    # 검색 기록
    st.subheader("📜 최근 검색")
    
    if st.session_state.search_history:
        for i, item in enumerate(reversed(st.session_state.search_history[-5:]), 1):
            with st.container():
                st.markdown(f"**Q{i}:** {item['question'][:50]}...")
                if st.button(f"다시 보기", key=f"history_{i}"):
                    st.info(item['answer'])
                st.divider()
    else:
        st.info("아직 검색 기록이 없습니다")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <small>
        Slack Q&A Search v1.0.0 | 
        Powered by OpenAI & ChromaDB | 
        <a href='https://github.com/yourrepo' target='_blank'>GitHub</a>
        </small>
    </div>
    """,
    unsafe_allow_html=True
)