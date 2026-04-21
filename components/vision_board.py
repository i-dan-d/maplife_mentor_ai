import streamlit as st
import json
from datetime import datetime, timedelta
from core.openai_client import OpenAIClient
from core.supabase_client import SupabaseClient

def get_days_left(created_at_str, timeframe_str):
    """Tính toán số ngày còn lại dựa trên thời gian tạo lộ trình"""
    try:
        # Xử lý chuỗi thời gian từ Supabase (bỏ phần microsecond và timezone)
        created_at = datetime.strptime(created_at_str.split('.')[0].replace('T', ' '), "%Y-%m-%d %H:%M:%S")
        
        # Ước lượng số ngày
        days_to_add = 365
        if "6" in timeframe_str: days_to_add = 180
        elif "2" in timeframe_str: days_to_add = 730
        elif "3" in timeframe_str: days_to_add = 1095
            
        target_date = created_at + timedelta(days=days_to_add)
        days_left = (target_date - datetime.utcnow()).days
        return max(0, days_left)
    except Exception:
        return 365 # Mặc định nếu lỗi

def vision_board():
    st.header("🎯 Bảng Tầm Nhìn (Vision Board)")
    
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Vui lòng đăng nhập để xem Bảng tầm nhìn.")
        return

    db_client = SupabaseClient()
    ai_client = OpenAIClient()

    # ==========================================
    # 1. THU THẬP DỮ LIỆU ĐỂ LÀM MỎ NEO
    # ==========================================
    roadmaps = db_client.query_data("user_roadmaps", filters={"user_id": user_id}) or []
    if not roadmaps:
        st.info("💡 Bạn cần tạo Lộ trình sự nghiệp trước khi xây dựng Vision Board!")
        return
        
    latest_roadmap = sorted(roadmaps, key=lambda x: x['created_at'], reverse=True)[0]
    target_role = latest_roadmap.get('target_role', 'Mục tiêu của bạn')
    timeframe = latest_roadmap.get('timeframe', '1 Năm')
    created_at = latest_roadmap.get('created_at', '')

    # ==========================================
    # 2. KHU VỰC TRUYỀN CẢM HỨNG (METRICS & AI QUOTE)
    # ==========================================
    days_left = get_days_left(created_at, timeframe)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        st.metric(label="Đích đến", value=target_role)
    with col2:
        st.metric(label="Thời gian còn lại", value=f"{days_left} ngày", delta="-1 ngày hôm nay", delta_color="inverse")
    with col3:
        # AI tự động sinh Quote mỗi khi load trang (có thể lưu session_state để đỡ tốn token)
        if "daily_quote" not in st.session_state:
            with st.spinner("AI đang tìm lời khuyên cho bạn..."):
                prompt = f"Viết 1 câu châm ngôn truyền cảm hứng (dưới 30 chữ) dành riêng cho một người đang nỗ lực vươn tới vị trí {target_role}."
                quote = ai_client.generate_response([{"role": "user", "content": prompt}], max_tokens=100)
                st.session_state.daily_quote = quote.strip('"')
                
        st.info(f"✨ *\"{st.session_state.daily_quote}\"*")

    st.divider()

    # ==========================================
    # 3. BẢNG GHIM (STICKY NOTES)
    # ==========================================
    st.subheader("📌 Bảng ghim mục tiêu của bạn")
    
    # Khu vực thêm ghi chú mới
    with st.form("add_note_form", clear_on_submit=True):
        col_text, col_btn = st.columns([4, 1])
        with col_text:
            new_note = st.text_input("Thêm lời nhắc, thói quen hoặc mục tiêu nhỏ (VD: 'Dậy sớm lúc 6h', 'Đọc 1 trang sách')...")
        with col_btn:
            submitted = st.form_submit_button("Ghim lên bảng", use_container_width=True)
            
        if submitted and new_note:
            db_client.insert_data("documents", {
                "content": new_note,
                "metadata": {"user_id": user_id, "source": "vision_note"}
            })
            st.toast("Đã ghim thành công!", icon="📌")
            st.rerun()

    # Lấy danh sách ghi chú từ Database
    all_notes = db_client.query_data("documents", filters={"metadata->>user_id": user_id, "metadata->>source": "vision_note"}) or []
    
    if not all_notes:
        st.caption("Bảng của bạn đang trống. Hãy ghim mục tiêu đầu tiên lên nhé!")
    else:
        # Vẽ giao diện dạng lưới (Grid 3 cột)
        cols = st.columns(3)
        for idx, note in enumerate(all_notes):
            col = cols[idx % 3] # Phân bổ đều ghi chú vào 3 cột
            with col:
                # Dùng Custom HTML/CSS để tạo giao diện Sticky Note
                st.markdown(f"""
                <div style="
                    background-color: #fffacd; 
                    padding: 15px; 
                    border-radius: 5px; 
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                    margin-bottom: 15px;
                    border-left: 5px solid #ffd700;
                    color: #333;
                ">
                    <b>📍</b> {note.get('content')}
                </div>
                """, unsafe_allow_html=True)
                
                # Nút xóa nhỏ ở dưới mỗi ghi chú
                if st.button("Xóa", key=f"del_note_{note.get('id')}", use_container_width=True):
                    db_client.delete_data("documents", {"id": note.get("id")})
                    st.rerun()