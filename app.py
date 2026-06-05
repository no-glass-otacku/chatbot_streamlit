import os
import streamlit as st
from openai import AzureOpenAI

# ── 환경 설정 ──────────────────────────────────────────────
# from dotenv import load_dotenv
# load_dotenv()

# endpoint        = os.getenv("ENDPOINT_URL")
# deployment      = os.getenv("DEPLOYMENT_NAME")
# search_endpoint = os.getenv("SEARCH_ENDPOINT")
# search_key      = os.getenv("SEARCH_KEY")
# search_index    = os.getenv("SEARCH_INDEX_NAME")
# subscription_key= os.getenv("AZURE_OPENAI_API_KEY")

# embedding_endpoint = os.getenv("EMBEDDING_ENDPOINT")
# embedding_key = os.getenv("EMBEDDING_KEY")

import streamlit as st

endpoint         = st.secrets["ENDPOINT_URL"]
deployment       = st.secrets["DEPLOYMENT_NAME"]
search_endpoint  = st.secrets["SEARCH_ENDPOINT"]
search_key       = st.secrets["SEARCH_KEY"]
search_index     = st.secrets["SEARCH_INDEX_NAME"]
subscription_key = st.secrets["AZURE_OPENAI_API_KEY"]

embedding_endpoint = st.secrets["EMBEDDING_ENDPOINT"]
embedding_key = st.secrets["EMBEDDING_KEY"]

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2025-01-01-preview",
)

SYSTEM_PROMPT = """당신은 서울과학기술대학교 교내 이동수단 규정 안내 챗봇입니다.

        [답변 규칙]
        1. 제공된 검색 결과(citations)에 있는 내용을 적극적으로 활용해서 답변하세요.
        2. citations에 관련 내용이 있으면 반드시 해당 내용을 바탕으로 답변하세요.
        3. citations에 관련 내용이 전혀 없을 때만 "해당 규정을 찾을 수 없습니다"라고 답하세요.

        [용어 안내 규칙]
        - "자전거"로 질문이 들어오면 답변 앞에 아래 내용을 추가하세요:
        "⚠️ 서울과기대 규정에서 일반 자전거에 대한 별도 규정은 없습니다.
        전동킥보드·전동자전거 등은 '개인형 이동장치'로 분류되며,
        관련 규정을 안내해 드리겠습니다." """


def chatbot(user_input: str):
    """(content, citations) 튜플 반환"""
    completion = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_input},
        ],
        max_tokens=2000,
        temperature=0,
        stream=False,
        extra_body={
            "data_sources": [{
                "type": "azure_search",
                "parameters": {
                    "endpoint":               search_endpoint,
                    "index_name":             search_index,
                    "semantic_configuration": f"{search_index}-semantic-configuration",
                    "query_type": "vector_semantic_hybrid",
                    "embedding_dependency": {
                        "type": "endpoint",
                        "endpoint": embedding_endpoint,
                        "authentication": {
                            "type": "api_key",
                            "key": embedding_key
                        }
                    },
                    "fields_mapping":         {},
                    "in_scope":               True,
                    "filter":                 None,
                    "strictness":             3,
                    "top_n_documents":        5,
                    "authentication": {
                        "type": "api_key",
                        "key":  search_key,
                    },
                },
            }],
        },
    )
    content   = completion.choices[0].message.content
    citations = (
        completion.choices[0].message.context.get("citations", [])
        if hasattr(completion.choices[0].message, "context")
        and completion.choices[0].message.context
        else []
    )
    return content, citations


# ── Streamlit 페이지 설정 ──────────────────────────────────
st.set_page_config(
    page_title="서울과기대 이동수단 규정 챗봇",
    page_icon="🛴",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

.main-header {
    background: linear-gradient(135deg, #1a3a5c 0%, #0d6efd 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
}
.main-header h1 { margin: 0; font-size: 1.6rem; font-weight: 700; }
.main-header p  { margin: 0.3rem 0 0; font-size: 0.9rem; opacity: 0.85; }

.chat-user {
    background: #0d6efd;
    color: white;
    padding: 0.8rem 1.1rem;
    border-radius: 18px 18px 4px 18px;
    margin: 0.5rem 0 0.5rem 3rem;
    font-size: 0.95rem;
    line-height: 1.5;
}
.chat-bot {
    background: #f1f3f5;
    color: #212529;
    padding: 0.8rem 1.1rem;
    border-radius: 18px 18px 18px 4px;
    margin: 0.5rem 3rem 0.5rem 0;
    font-size: 0.95rem;
    line-height: 1.6;
    border-left: 3px solid #0d6efd;
}

.citation-card {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.7rem;
    font-size: 0.85rem;
}
.citation-title {
    font-weight: 700;
    color: #1a3a5c;
    margin-bottom: 0.4rem;
    font-size: 0.8rem;
}
.citation-content {
    color: #495057;
    line-height: 1.6;
    white-space: pre-wrap;
    word-break: break-word;
}

.sidebar-header {
    font-weight: 700;
    font-size: 0.95rem;
    color: #1a3a5c;
    padding: 0.5rem 0;
    border-bottom: 2px solid #0d6efd;
    margin-bottom: 1rem;
}

.example-section {
    margin-bottom: 1.2rem;
}
.example-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}
div[data-testid="stButton"] > button[kind="secondary"] {
    background: #f8f9ff;
    border: 1px solid #c5d0f0;
    border-radius: 20px;
    color: #1a3a5c;
    font-size: 0.82rem;
    padding: 0.3rem 0.8rem;
    margin: 0.15rem 0;
    transition: all 0.15s;
    text-align: left;
    white-space: normal;
    height: auto;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #e8eeff;
    border-color: #0d6efd;
    color: #0d6efd;
}
</style>
""", unsafe_allow_html=True)

# ── 세션 초기화 ───────────────────────────────────────────
if "messages"  not in st.session_state:
    st.session_state.messages  = []   # {"role", "content"}
if "citations" not in st.session_state:
    st.session_state.citations = []   # 마지막 응답의 citations
if "example_input" not in st.session_state:
    st.session_state.example_input = ""  # 예시 질문 클릭 시 입력창에 채울 값


# ── 레이아웃 ──────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>🛴 서울과기대 이동수단 규정 안내</h1>
  <p>개인형 이동장치 및 캠퍼스 교통관리 규정을 검색해 드립니다</p>
</div>
""", unsafe_allow_html=True)

chat_col, source_col = st.columns([3, 2])

# ── 채팅 영역 ─────────────────────────────────────────────
with chat_col:
    chat_container = st.container(height=520)

    with chat_container:
        if not st.session_state.messages:
            st.markdown(
                "<div style='text-align:center;color:#adb5bd;margin-top:6rem;font-size:0.95rem;'>"
                "💬 질문을 입력하면 관련 규정을 찾아드립니다<br>"
                "<small>예: 개인형 이동장치 주차 금지 구역은?</small>"
                "</div>",
                unsafe_allow_html=True,
            )
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="chat-user">{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="chat-bot">{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )

    # 예시 질문
    EXAMPLES = {
        "🛴 개인형 이동장치": [
            "개인형 이동장치 주차 금지 구역은 어디인가요?",
            "전동킥보드 속도 제한은 몇 km/h인가요?",
            "음주 상태에서 개인형 이동장치를 타면 안 되나요?",
            "개인형 이동장치 충전은 어디서 할 수 있나요?",
        ],
        "🚗 캠퍼스 주차": [
            "학생도 정기주차를 신청할 수 있나요?",
            "주차료 할인을 받을 수 있는 차량은?",
            "교내에서 주차가 금지된 장소는 어디인가요?",
            "정기주차 등록에 필요한 서류는 무엇인가요?",
        ],
    }

    st.markdown('<div class="example-section">', unsafe_allow_html=True)
    for category, questions in EXAMPLES.items():
        st.markdown(f'<div class="example-label">{category}</div>', unsafe_allow_html=True)
        for q in questions:
            if st.button(q, key=f"ex_{q}", use_container_width=True):
                st.session_state.example_input = q

    st.markdown('</div>', unsafe_allow_html=True)

    # 예시 질문이 클릭됐으면 바로 전송 처리
    if st.session_state.example_input:
        selected = st.session_state.example_input
        st.session_state.example_input = ""
        st.session_state.messages.append({"role": "user", "content": selected})
        with st.spinner("규정을 검색 중입니다..."):
            answer, citations = chatbot(selected)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.citations = citations
        st.rerun()

    # 입력창
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_input = st.text_input(
                "질문 입력",
                placeholder="예: 전동킥보드 속도 제한은?",
                label_visibility="collapsed",
            )
        with col_btn:
            submitted = st.form_submit_button("전송", use_container_width=True)

    if submitted and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("규정을 검색 중입니다..."):
            answer, citations = chatbot(user_input)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.citations = citations
        st.rerun()

# ── 출처 문서 영역 ────────────────────────────────────────
with source_col:
    st.markdown('<div class="sidebar-header">📂 참조된 원본 문서</div>', unsafe_allow_html=True)

    if not st.session_state.citations:
        st.markdown(
            "<div style='color:#adb5bd;font-size:0.9rem;margin-top:1rem;'>"
            "질문을 하면 검색에 사용된 원본 규정 문서가 여기에 표시됩니다."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        # 중복 제거 (같은 chunk_id + title)
        seen = set()
        unique = []
        for c in st.session_state.citations:
            key = (c.get("title",""), c.get("chunk_id",""))
            if key not in seen:
                seen.add(key)
                unique.append(c)

        st.markdown(f"<small style='color:#6c757d;'>총 {len(unique)}개 청크 참조됨</small>", unsafe_allow_html=True)

        for i, c in enumerate(unique, 1):
            title   = c.get("title",   "출처 불명")
            content = c.get("content", "")
            chunk_id= c.get("chunk_id","")

            with st.expander(f"📄 {i}. {title}  (chunk {chunk_id})", expanded=(i == 1)):
                st.markdown(
                    f'<div class="citation-content">{content}</div>',
                    unsafe_allow_html=True,
                )

    # 대화 초기화 버튼
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages  = []
        st.session_state.citations = []
        st.rerun()
