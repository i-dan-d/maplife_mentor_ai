import streamlit as st

def setup_page_css():
    """Hàm tiêm CSS 'Premium' để lột xác toàn bộ giao diện MAPLIFE"""
    custom_css = """
    <style>
    /* 1. Tạo nền Gradient mượt mà cho toàn bộ App */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #E8F5E9 0%, #FFFFFF 50%, #F1F3F4 100%);
        background-attachment: fixed;
    }

    /* 2. Triệt tiêu Padding thừa và làm sạch Header */
    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
    }
    [data-testid="stHeader"] { display: none; }

    /* 3. PHONG CÁCH CARD UI: Biến các khối nội dung thành 'Thẻ' nổi */
    /* Áp dụng cho các container, form và các khối thông tin */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        /* Chỉ áp dụng cho các khối nội dung lớn */
    }

    /* CSS cho khung đăng nhập và các thẻ component */
    .custom-card {
        background-color: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.3);
        margin-bottom: 20px;
    }

    /* 4. HIỆU ỨNG ĐỘNG CHO NÚT BẤM (Hover Animation) */
    .stButton>button {
        border-radius: 12px !important;
        padding: 0.5rem 1rem !important;
        background-color: white !important;
        color: #2E7D32 !important;
        border: 1px solid #2E7D32 !important;
        font-weight: 600 !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    
    .stButton>button:hover {
        background-color: #2E7D32 !important;
        color: white !important;
        transform: scale(1.05) translateY(-3px);
        box-shadow: 0 8px 20px rgba(46, 125, 50, 0.3) !important;
    }

    /* Hiệu ứng cho tab */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        background-color: rgba(255, 255, 255, 0.5);
    }

    /* Tùy chỉnh thanh cuộn cho hiện đại */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #cbd5e0; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #2E7D32; }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)