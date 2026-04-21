import streamlit as st
from core.supabase_client import SupabaseClient

def sign_up_user(email, password):
    """Đăng ký tài khoản mới trên Supabase"""
    db = SupabaseClient()
    try:
        response = db.client.auth.sign_up({
            "email": email,
            "password": password,
        })
        return response
    except Exception as e:
        st.error(f"Lỗi đăng ký: {str(e)}")
        return None

def sign_in_user(email, password):
    """Đăng nhập tài khoản hiện có"""
    db = SupabaseClient()
    try:
        response = db.client.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
        return response
    except Exception as e:
        st.error(f"Lỗi đăng nhập: {str(e)}")
        return None