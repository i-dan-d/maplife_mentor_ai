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
def reset_password(email: str):
    """Gửi email chứa liên kết đặt lại mật khẩu qua Supabase"""
    try:
        db = SupabaseClient()
        # Hàm của Supabase để gửi link reset password
        db.client.auth.reset_password_for_email(email)
        return True, "Vui lòng kiểm tra hộp thư email (cả thư mục Spam) để đặt lại mật khẩu!"
    except Exception as e:
        # Xử lý thông báo lỗi thân thiện hơn
        error_msg = str(e)
        if "User not found" in error_msg:
            return False, "Email này chưa được đăng ký trong hệ thống."
        elif "rate_limit" in error_msg.lower():
            return False, "Bạn đã yêu cầu quá nhiều lần. Vui lòng thử lại sau ít phút."
        return False, f"Lỗi hệ thống: {error_msg}"
def update_password(new_password: str):
    try:
        db = SupabaseClient()
        # Supabase tự hiểu token từ URL để thực hiện lệnh này
        db.client.auth.update_user({"password": new_password})
        return True, "Mật khẩu đã được cập nhật thành công!"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"