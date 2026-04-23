import streamlit as st

def setup_page_css():
    """Hàm tiêm CSS custom để lột xác giao diện Streamlit"""
    custom_css = """
    <style>
    /* 1. Triệt tiêu khoảng trống phía trên cùng và mở rộng hai bên */
    .main .block-container {
        padding-top: 1.5rem !important; /* Vừa đủ để không bị dính sát viền màn hình */
        padding-bottom: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        max-width: 100% !important;
    }
    
    /* 2. Ẩn các thành phần mặc định của Streamlit */
    [data-testid="stHeader"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 3. Làm mượt Nút bấm (Buttons) */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(46, 125, 50, 0.2) !important;
    }
    
    /* 4. Làm đẹp các ô nhập liệu (Inputs) */
    .stTextInput>div>div>input {
        border-radius: 6px !important;
    }
    
    /* 5. Khung bao bọc cho phần Form Đăng nhập (Canh giữa) */
    .login-wrapper {
        background-color: white; 
        padding: 2rem; 
        border-radius: 12px; 
        box-shadow: 0 8px 16px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)