import streamlit as st
from streamlit_option_menu import option_menu
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
# --- BẮT ĐẦU CẤP ĐỘ 2: CUSTOM CSS ---
hide_st_style = """
    <style>
    /* Ẩn Header, Menu mặc định và Footer của Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Làm đẹp Nút bấm (Bo góc, hiệu ứng nổi lên khi di chuột) */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(46, 125, 50, 0.2); /* Đổ bóng màu xanh */
    }
    
    /* Làm đẹp các khung nhập liệu */
    .stTextInput>div>div>input {
        border-radius: 6px;
    }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
# --- KẾT THÚC CẤP ĐỘ 2 ---
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
    # 1. GIAO DIỆN ĐĂNG NHẬP (CANH GIỮA MÀN HÌNH)
    # ==========================================
    if st.session_state.auth_user is None:
        # Tạo khoảng trống phía trên để đẩy form xuống giữa
        st.write("")
        st.write("")
        
        # Tiêu đề Canh giữa
        st.markdown("<h1 style='text-align: center; color: #2E7D32;'>🌱 MAPLIFE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 18px; color: #666;'>AI Personal Career Mentor</p>", unsafe_allow_html=True)
        st.write("")
        
        # Dùng st.columns để ép form vào giữa (Tỉ lệ 1 : 1.2 : 1)
        col1, col2, col3 = st.columns([1, 1.2, 1])
        
        with col2:
            st.markdown("<div style='background-color: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
            tab_login, tab_signup = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký"])
            
            with tab_login:
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Mật khẩu", type="password", key="login_pass")
                if st.button("Đăng nhập", use_container_width=True):
                    res = sign_in_user(email, password)
                    if res and res.user:
                        user_id = res.user.id
                        existing_user = db.query_data("users", filters={"id": user_id})
                        if not existing_user:
                            db.insert_data("users", {
                                "id": user_id, "name": email.split("@")[0], "email": email, "profile_data": {}
                            })
                        
                        cookie_manager.set(
                            "maplife_access_token", res.session.access_token, 
                            max_age=604800, secure=True, same_site="none", key="login_cookie"
                        )
                        st.session_state.auth_user = res.user
                        st.session_state.user_id = res.user.id
                        
                        st.success("Đang thiết lập phiên đăng nhập...")
                        time.sleep(1.5) 
                        st.rerun()
                        
            with tab_signup:
                new_email = st.text_input("Email", key="reg_email")
                new_pass = st.text_input("Mật khẩu", type="password", key="reg_pass")
                if st.button("Tạo tài khoản", use_container_width=True):
                    res = sign_up_user(new_email, new_pass)
                    if res and res.user:
                        db.insert_data("users", {
                            "id": res.user.id, "name": new_email.split("@")[0], "email": new_email, "profile_data": {}
                        })
                        st.success("Đăng ký thành công! Hãy chuyển sang tab Đăng nhập.")
            st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # 2. GIAO DIỆN CHÍNH (TOP NAVIGATION MENU)
    # ==========================================
    else:
        # Header: Logo bên trái, Xin chào & Đăng xuất bên phải
        header_col1, header_col2, header_col3 = st.columns([1, 4, 1])
        with header_col1:
            st.markdown("<h3 style='color: #2E7D32; margin-top: 0;'>🌱 MAPLIFE</h3>", unsafe_allow_html=True)
        with header_col3:
            st.write(f"👋 **{st.session_state.auth_user.email.split('@')[0]}**")
            if st.button("🚪 Đăng xuất", use_container_width=True):
                cookie_manager.delete("maplife_access_token", key="logout_cookie")
                st.session_state.clear()
                time.sleep(1.5)
                st.rerun()

        # Thanh Menu Ngang (Horizontal)
        choice = option_menu(
            menu_title=None,  # Ẩn tiêu đề để menu nằm ngang đẹp hơn
            options=["AI Chat", "Tính cách", "Hồ sơ CV", "Lộ trình", "Tiến độ", "Vision Board"],
            icons=["chat-quote-fill", "person-lines-fill", "file-earmark-person", "map-fill", "bar-chart-steps", "easel-fill"],
            default_index=0,
            orientation="horizontal", # <-- PHÉP MÀU NẰM Ở ĐÂY
            styles={
                "container": {"padding": "0!important", "max-width": "100%", "border-radius": "8px", "background-color": "#ffffff", "border": "1px solid #eee"},
                "icon": {"color": "#2E7D32", "font-size": "16px"}, 
                "nav-link": {
                    "font-size": "14px", 
                    "text-align": "center", 
                    "margin":"0px", 
                    "--hover-color": "#E8F5E9"
                },
                "nav-link-selected": {
                    "background-color": "#2E7D32", 
                    "color": "white", 
                    "font-weight": "bold"
                },
            }
        )
        
        st.divider() # Đường kẻ phân cách menu và nội dung
        
        # Gọi Component tương ứng
        if choice == "AI Chat":
            chat_interface()
        elif choice == "Tính cách":
            personality_test()
        elif choice == "Hồ sơ CV":
            cv_analyzer()
        elif choice == "Lộ trình":
            roadmap()
        elif choice == "Tiến độ":
            progress_tracker()
        elif choice == "Vision Board":
            vision_board()
# Bắt đầu chạy ứng dụng (Không còn code test)
if __name__ == "__main__":
    main()
