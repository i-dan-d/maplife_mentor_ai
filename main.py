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
from components.community import community_board
from core.supabase_client import SupabaseClient
from utils.auth import sign_up_user, sign_in_user
from utils.ui_factory import setup_page_css
# Các imports components giữ nguyên...
# Cấu hình trang cơ bản
st.set_page_config(
    page_title="Map Life", 
    page_icon="🌱", 
    layout="wide",
    initial_sidebar_state="collapsed" #ép mở sidebar
)
def render_reset_password_form():
    """Vẽ giao diện Đặt lại mật khẩu mới khi user click từ Email"""
    st.write("")
    st.write("")
    
    st.markdown("<h1 style='text-align: center; color: #2E7D32;'>🌱 MAPLIFE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px; color: #666;'>Tạo mật khẩu mới của bạn</p>", unsafe_allow_html=True)
    st.write("")
    
    # Căn giữa form giống hệt trang đăng nhập
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        with st.container(border=True):
            st.info("💡 Mã xác thực từ email đã được ghi nhận. Vui lòng nhập mật khẩu mới.")
            
            new_password = st.text_input("Mật khẩu mới (Tối thiểu 6 ký tự)", type="password", key="reset_new_pass")
            confirm_password = st.text_input("Xác nhận mật khẩu", type="password", key="reset_confirm_pass")
            
            st.write("")
            if st.button("💾 Lưu mật khẩu & Đăng nhập", type="primary", use_container_width=True):
                if not new_password or not confirm_password:
                    st.warning("Vui lòng điền đầy đủ thông tin.")
                elif new_password != confirm_password:
                    st.error("Mật khẩu xác nhận không khớp!")
                elif len(new_password) < 6:
                    st.warning("Mật khẩu quá ngắn. Vui lòng nhập ít nhất 6 ký tự.")
                else:
                    with st.spinner("Đang cập nhật vào hệ thống bảo mật..."):
                        # Gọi hàm update từ utils.auth
                        from utils.auth import update_password
                        success, msg = update_password(new_password)
                        
                        if success:
                            st.success(msg)
                            st.balloons()
                            import time
                            time.sleep(2)
                            # Thành công thì xóa trạng thái reset để quay về màn hình Login
                            st.session_state.reset_mode = False
                            st.query_params.clear() # Xóa luôn param trên thanh địa chỉ cho sạch
                            st.rerun()
                        else:
                            st.error(msg)
            
            st.divider()
            # Nút "Quay xe" nếu người dùng đổi ý hoặc click nhầm link
            if st.button("Trở về trang Đăng nhập", use_container_width=True):
                st.session_state.reset_mode = False
                st.query_params.clear()
                st.rerun()
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
    setup_page_css()
    db = SupabaseClient()
    
    # Khởi tạo cookie manager
    cookie_manager = stx.CookieManager(key="maplife_cookie_mgr")
    query_params = st.query_params

    # Kiểm tra xem có phải người dùng quay về từ link Reset Password không
    # Supabase thường trả về tham số type=recovery hoặc access_token
    if "type" in query_params and query_params["type"] == "recovery":
        st.session_state.reset_mode = True

    if st.session_state.get("reset_mode"):
        render_reset_password_form() # Hàm vẽ form đặt lại mật khẩu
        st.stop() # Dừng các phần login/menu khác lại
    # ==========================================
    # 🟢 BẮT ĐẦU FIX LỖI MẤT MENU (MÀN HÌNH CHỜ)
    # ==========================================
    if "app_loaded" not in st.session_state:
        # Hiện dòng chữ chờ để trình duyệt kịp nạp Cookie về Python
        st.markdown("<h3 style='text-align: center; color: #2E7D32; margin-top: 50px;'>🌱 MAPLIFE đang khôi phục dữ liệu...</h3>", unsafe_allow_html=True)
        time.sleep(0.5) # Dừng 0.5 giây
        st.session_state.app_loaded = True
        st.rerun() # Chạy lại để load giao diện chính thức
    # ==========================================
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
        st.markdown("<p style='text-align: center; font-size: 18px; color: #666;'>DFI2026_NHÓM 3_MAPLIFE_Demo</p>", unsafe_allow_html=True)
        st.write("")
        
        # Dùng st.columns để ép form vào giữa (Tỉ lệ 1 : 1.2 : 1)
        col1, col2, col3 = st.columns([1, 1.2, 1])
        
        with col2:
            with st.container(border=True): 
                tab_login, tab_signup, tab_forgot = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký", "🆘 Quên mật khẩu"])
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
            with tab_forgot:
                st.markdown("### Khôi phục mật khẩu")
                st.caption("Nhập email bạn đã dùng để đăng ký. MAPLIFE sẽ gửi cho bạn một liên kết an toàn để đặt lại mật khẩu mới.")
                
                forgot_email = st.text_input("Email của bạn", key="forgot_email_input")
                
                if st.button("Gửi liên kết khôi phục", type="primary", use_container_width=True):
                    if not forgot_email:
                        st.warning("Vui lòng nhập email trước khi gửi.")
                    else:
                        with st.spinner("Đang gửi yêu cầu..."):
                            # Nhớ import hàm reset_password từ utils.auth ở đầu file main.py nhé!
                            from utils.auth import reset_password 
                            success, msg = reset_password(forgot_email)
                            
                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)
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
            options=["AI Chat", "Tính cách", "Hồ sơ CV", "Lộ trình", "Tiến độ", "Vision Board", "Community"],
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
        elif choice == "Community":
            community_board()
# Bắt đầu chạy ứng dụng (Không còn code test)
if __name__ == "__main__":
    main()
