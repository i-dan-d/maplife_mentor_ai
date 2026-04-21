import streamlit as st
import extra_streamlit_components as stx
import time
# Import các components
from components.chat import chat_interface
from components.personality_test import personality_test
from components.cv_analyzer import cv_analyzer
from components.roadmap import roadmap
from components.progress import progress_tracker
from components.vision_board import vision_board
from core.supabase_client import SupabaseClient
from utils.auth import sign_up_user, sign_in_user

# Các imports components giữ nguyên...
# Cấu hình trang cơ bản
st.set_page_config(
    page_title="Map Life", 
    page_icon="🌱", 
    layout="wide"
)
def main():
    # =============== BẮT ĐẦU CHẾ ĐỘ X-QUANG ===============
    # st.title("🛠 Chế độ Debug X-Quang")
    # st.warning("Đang kiểm tra kho báu Secrets trên server...")
    
    # try:
    #     # Kiểm tra xem server có thấy mục Secrets không
    #     keys = list(st.secrets.keys())
    #     st.write("1. Các chìa khóa server đang cầm:", keys)
        
    #     # Kiểm tra xem file config đang nhận giá trị gì
    #     from config.config import SUPABASE_URL
    #     st.write("2. File config.py đang đọc ra URL là:", "CÓ DỮ LIỆU" if SUPABASE_URL else "RỖNG (NONE)")
        
    # except Exception as e:
    #     st.error(f"Lỗi hệ thống khi đọc Secrets: {e}")
        
    # st.stop() # BẮT BUỘC CÓ DÒNG NÀY: Dừng app lại ngay lập tức để không bị văng lỗi
    # =============== KẾT THÚC CHẾ ĐỘ X-QUANG ===============
    db = SupabaseClient()
    st.sidebar.title("🌱 MAPLIFE")
    st.sidebar.caption("AI Personal Career Mentor")
    st.sidebar.divider()
    # Khởi tạo cookie manager
    cookie_manager = stx.CookieManager(key="maplife_cookie_mgr")
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None
    if st.session_state.auth_user is None:
        saved_token = cookie_manager.get("maplife_access_token")
        if saved_token:
            try:
                res = db.client.auth.get_user(saved_token)
                if res and res.user:
                    st.session_state.auth_user = res.user
                    st.session_state.user_id = res.user.id
            except:
                cookie_manager.delete("maplife_access_token")

    # ==========================================
    # 3. GIAO DIỆN SIDEBAR AUTH
    # ==========================================
    with st.sidebar:
        if st.session_state.auth_user is None: # <--- Dòng này sẽ không bao giờ lỗi nữa
            st.subheader("🔑 Xác thực")
            tab_login, tab_signup = st.tabs(["Đăng nhập", "Đăng ký"])
            
            with tab_login:
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Mật khẩu", type="password", key="login_pass")
                if st.button("Đăng nhập", use_container_width=True):
                    res = sign_in_user(email, password)
                    
                    # Chỉ cần 1 lần kiểm tra if duy nhất ở đây
                    if res and res.user:
                        user_id = res.user.id
                        
                        # --- KIỂM TRA VÀ ĐỒNG BỘ DATABASE ---
                        existing_user = db.query_data("users", filters={"id": user_id})
                        if not existing_user:
                            db.insert_data("users", {
                                "id": user_id,
                                "name": email.split("@")[0],
                                "email": email,
                                "profile_data": {}
                            })
                        # ---------------------------------
                        
                        # Lưu Cookie & Session
                        cookie_manager.set("maplife_access_token", res.session.access_token, max_age=604800)
                        
                        st.session_state.auth_user = res.user
                        st.session_state.user_id = res.user.id
                        
                        # ÉP STREAMLIT CHỜ TRÌNH DUYỆT LƯU COOKIE XONG MỚI RERUN
                        time.sleep(0.5) 
                        st.rerun()
            with tab_signup:
                new_email = st.text_input("Email", key="reg_email")
                new_pass = st.text_input("Mật khẩu", type="password", key="reg_pass")
                if st.button("Tạo tài khoản", use_container_width=True):
                    res = sign_up_user(new_email, new_pass)
                    if res and res.user:
                        user_id = res.user.id
                        
                        # --- ĐOẠN CODE BỔ SUNG FIX LỖI ---
                        # Ngay khi đăng ký thành công, lưu thẳng vào bảng 'users'
                        db.insert_data("users", {
                            "id": user_id,
                            "name": new_email.split("@")[0],
                            "email": new_email,
                            "profile_data": {}
                        })
                        # ---------------------------------
                        
                        st.success("Đăng ký thành công! Hãy chuyển sang tab Đăng nhập.")
        else:
            st.success(f"Chào, {st.session_state.auth_user.email}")
            if st.button("🚪 Đăng xuất", use_container_width=True):
                cookie_manager.delete("maplife_access_token")
                st.session_state.clear()
                time.sleep(0.5)
                st.rerun()
        st.divider()

    # 3. Chỉ hiển thị Menu nếu đã đăng nhập
    if st.session_state.auth_user:
        # Gộp tất cả tính năng vào đây
        menu_options = [
            "💬 AI Mentor Chat", 
            "🧪 Trắc nghiệm tính cách", 
            "📄 Xây dựng Hồ sơ CV", 
            "🛤️ Lộ trình sự nghiệp", 
            "📊 Tiến độ", 
            "🎯 Vision Board"
        ]
        choice = st.sidebar.radio("Điều hướng", menu_options)
        
        st.divider()
        
        # ĐIỀU HƯỚNG GIAO DIỆN (Routing)
        if choice == "💬 AI Mentor Chat":
            chat_interface()
        elif choice == "🧪 Trắc nghiệm tính cách":
            personality_test()
        elif choice == "📄 Xây dựng Hồ sơ CV":
            cv_analyzer()
        elif choice == "🛤️ Lộ trình sự nghiệp":
            roadmap()
        elif choice == "📊 Tiến độ":
            progress_tracker()
        elif choice == "🎯 Vision Board":
            vision_board()

    else:
        st.info("👋 Chào mừng bạn đến với MAPLIFE. Vui lòng đăng nhập từ Sidebar để bắt đầu hành trình sự nghiệp.")
# Bắt đầu chạy ứng dụng (Không còn code test)
if __name__ == "__main__":
    main()
