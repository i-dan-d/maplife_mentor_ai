"""
Configuration module for MAPLIFE application
"""
import os
import streamlit as st
from dotenv import load_dotenv

# Vẫn load file .env cho môi trường Local
load_dotenv()

# ================ HÀM LẤY API KEY THÔNG MINH ================
def get_secret(key_name, default_value=None):
    """
    Tự động nhận diện môi trường:
    1. Tìm trong Streamlit Secrets (Khi deploy lên Cloud)
    2. Nếu không có, tìm trong Biến môi trường / .env (Khi chạy Local)
    """
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    
    return os.getenv(key_name, default_value)

# ================ OPENAI CONFIG ================
OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
OPENAI_BASE_URL = get_secret("OPENAI_BASE_URL", "https://platform.beeknoee.com/api/v1") 

OPENAI_MODEL = "claude-sonnet-4-6"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536

# ================ SUPABASE CONFIG ================
SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")

# ================ RAG CONFIG ================
RAG_TOP_K = 5
USE_LOCAL_FAISS = True
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# ================ STREAMLIT CONFIG ================
STREAMLIT_THEME = "light"
STREAMLIT_PAGE_ICON = "🌱"
STREAMLIT_LAYOUT = "wide"

# ================ APP CONFIG ================
APP_NAME = "MAPLIFE"
APP_DESCRIPTION = "AI Personal Career Mentor"
APP_VERSION = "1.0.0"

# ================ VALIDATION ================
def validate_config():
    """Validate required environment variables"""
    # Thay vì check os.getenv, ta check trực tiếp các biến đã lấy qua hàm get_secret
    missing = []
    if not OPENAI_API_KEY: missing.append("OPENAI_API_KEY")
    if not SUPABASE_URL: missing.append("SUPABASE_URL")
    if not SUPABASE_KEY: missing.append("SUPABASE_KEY")
    
    if missing:
        print(f"⚠️ Missing environment variables: {', '.join(missing)}")
        return False
    return True