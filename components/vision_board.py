import streamlit as st
import json
import random
from datetime import datetime, timedelta
from core.openai_client import OpenAIClient
from core.supabase_client import SupabaseClient

def calculate_time_metrics(created_at_str, timeframe_str):
    """Tính toán ngày còn lại và % tiến độ để vẽ thanh Progress"""
    try:
        created_at = datetime.strptime(created_at_str.split('.')[0].replace('T', ' '), "%Y-%m-%d %H:%M:%S")
        
        total_days = 365
        if "6" in timeframe_str: total_days = 180
        elif "2" in timeframe_str: total_days = 730
        elif "3" in timeframe_str: total_days = 1095
            
        target_date = created_at + timedelta(days=total_days)
        now = datetime.utcnow()
        
        days_left = max(0, (target_date - now).days)
        elapsed_days = max(0, total_days - days_left)
        progress_pct = min(1.0, elapsed_days / total_days)
        
        return days_left, progress_pct
    except Exception:
        return 365, 0.0

def vision_board():
    st.markdown("<h2 style='text-align: center; color: #2E7D32;'>✨ Bảng Tầm Nhìn (Vision Board)</h2>", unsafe_allow_html=True)
    
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
        st.info("💡 Bạn cần tạo Lộ trình sự nghiệp (Roadmap) trước khi xây dựng Vision Board!")
        return
        
    latest_roadmap = sorted(roadmaps, key=lambda x: x['created_at'], reverse=True)[0]
    target_role = latest_roadmap.get('target_role', 'Mục tiêu của bạn')
    timeframe = latest_roadmap.get('timeframe', '1 Năm')
    created_at = latest_roadmap.get('created_at', '')

    # Truy xuất thêm mã Holland (Tính cách) để cá nhân hóa lời chào
    personality_docs = db_client.query_data("documents", filters={"metadata->>user_id": user_id, "metadata->>source": "personality_test"})
    trait_greeting = "Chiến binh MAPLIFE"
    if personality_docs:
        try:
            p_data = json.loads(personality_docs[0]['content'])
            # Dựa vào chữ cái đầu của mã Holland
            primary = p_data.get("meta", {}).get("primary_trait", "R")
            traits_map = {"R": "Nhà Kỹ thuật", "I": "Nhà Nghiên cứu", "A": "Nhà Sáng tạo", "S": "Người Truyền cảm hứng", "E": "Nhà Lãnh đạo", "C": "Nhà Tổ chức"}
            trait_greeting = traits_map.get(primary, trait_greeting)
        except: pass

    # ==========================================
    # 2. KHU VỰC TRUYỀN CẢM HỨNG (HERO SECTION)
    # ==========================================
    st.markdown(f"<p style='text-align: center; font-size: 1.2rem; color: #666;'>Chào ngày mới, <b>{trait_greeting}</b>! Đích đến của bạn đang chờ phía trước.</p>", unsafe_allow_html=True)
    
    days_left, progress_pct = calculate_time_metrics(created_at, timeframe)
    
    with st.container(border=True):
        col1, col2 = st.columns([1, 2], gap="large")
        
        with col1:
            st.metric(label="Mục tiêu tối thượng", value=target_role)
            st.metric(label="Đồng hồ đếm ngược", value=f"{days_left} ngày", delta="-1 ngày so với hôm qua", delta_color="inverse")
            
        with col2:
            st.markdown(f"**⏳ Tiến độ thời gian ({int(progress_pct*100)}%)**")
            st.progress(progress_pct)
            
            # AI Quote Generator
            if "daily_quote" not in st.session_state:
                with st.spinner("Đang kết nối với vũ trụ để xin thông điệp..."):
                    prompt = f"Viết 1 câu châm ngôn truyền cảm hứng (dưới 25 chữ) dành riêng cho một người đang nỗ lực vươn tới vị trí {target_role}."
                    quote = ai_client.generate_response([{"role": "user", "content": prompt}], max_tokens=100)
                    st.session_state.daily_quote = quote.strip('"')
                    
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #E8F5E9, #C8E6C9); padding: 20px; border-radius: 15px; margin-top: 15px; border-left: 5px solid #2E7D32;">
                <h4 style="color: #2E7D32; font-style: italic; margin: 0;">"{st.session_state.daily_quote}"</h4>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ==========================================
    # 3. BẢNG GHIM MỤC TIÊU (MASONRY LAYOUT)
    # ==========================================
    st.subheader("📌 Bảng ghim mục tiêu & Thói quen")
    
    with st.form("add_note_form", clear_on_submit=True):
        col_text, col_btn = st.columns([4, 1])
        with col_text:
            new_note = st.text_input("Ghim một mục tiêu nhỏ, thói quen hoặc câu thần chú của bạn...")
        with col_btn:
            submitted = st.form_submit_button("📍 Ghim lên bảng", use_container_width=True)
            
        if submitted and new_note:
            db_client.insert_data("documents", {
                "content": new_note,
                "metadata": {"user_id": user_id, "source": "vision_note"}
            })
            st.toast("Đã ghim lên bảng tầm nhìn!", icon="📌")
            st.rerun()

    # Render Sticky Notes
    all_notes = db_client.query_data("documents", filters={"metadata->>user_id": user_id, "metadata->>source": "vision_note"}) or []
    
    if not all_notes:
        st.info("Bảng của bạn đang trống. Hãy ghim một mục tiêu nhỏ để khởi động nhé!")
    else:
        # Bảng màu Pastel cho Sticky Notes
        colors = ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF", "#E8C1A0"]
        
        cols = st.columns(3)
        for idx, note in enumerate(all_notes):
            col = cols[idx % 3] 
            note_color = colors[idx % len(colors)] # Chọn màu xoay vòng
            tilt = random.choice([-2, -1, 1, 2])   # Tạo độ nghiêng ngẫu nhiên cho giống note thật
            
            with col:
                st.markdown(f"""
                <div style="
                    background-color: {note_color}; 
                    padding: 20px; 
                    border-radius: 2px 15px 15px 15px; 
                    box-shadow: 3px 4px 10px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                    color: #333;
                    transform: rotate({tilt}deg);
                    font-weight: 500;
                    min-height: 120px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                ">
                    <span style="font-size: 1.2em;">📌 {note.get('content')}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Nút xóa đặt ngay dưới Note
                if st.button("🗑️ Gỡ thẻ", key=f"del_note_{note.get('id')}", use_container_width=True):
                    db_client.delete_data("documents", {"id": note.get("id")})
                    st.rerun()