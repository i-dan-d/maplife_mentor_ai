import streamlit as st

def setup_page_css():
    custom_css = """
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #E8F5E9 0%, #FFFFFF 50%, #F1F3F4 100%);
        background-attachment: fixed;
    }
    .main .block-container { padding-top: 1.5rem !important; max-width: 95% !important; }
    [data-testid="stHeader"] { display: none; }

    /* Biến st.container thành Card Glassmorphism */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05) !important;
        padding: 20px !important;
    }
    
    .stButton>button {
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: scale(1.03);
        box-shadow: 0 5px 15px rgba(46, 125, 50, 0.2) !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)