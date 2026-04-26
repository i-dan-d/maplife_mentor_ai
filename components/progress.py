import streamlit as st
import json
import random
from core.supabase_client import SupabaseClient
from components.sentiment_dashboard import render_sentiment_dashboard

def progress_tracker():
    st.markdown("<h2 style='text-align: center; color: #2E7D32;'>📊 Theo dõi Tiến độ (Progress Tracker)</h2>", unsafe_allow_html=True)

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Vui lòng đăng nhập để xem tiến độ của bạn.")
        return

    db_client = SupabaseClient()

    tab_progress, tab_sentiment = st.tabs(["📊 Mục tiêu & KPI", "💚 Sức khỏe Tinh thần"])
    
    with tab_progress:
        # ==========================================
        # 1. TRUY XUẤT LỘ TRÌNH MỚI NHẤT
        # ==========================================
        existing_roadmaps = db_client.query_data("user_roadmaps", filters={"user_id": user_id}) or []
        if not existing_roadmaps:
            st.info("💡 Bạn chưa có lộ trình nào để theo dõi. Hãy sang tab 'Lộ trình sự nghiệp' để tạo nhé!")
            # Không return luôn để user vẫn xem được tab sentiment nếu muốn
        else:
            latest_roadmap = sorted(existing_roadmaps, key=lambda x: x['created_at'], reverse=True)[0]
            roadmap_id = latest_roadmap['id']

            roadmap_json = latest_roadmap['roadmap_json']
            if isinstance(roadmap_json, str):
                try: roadmap_json = json.loads(roadmap_json)
                except: pass

            # ==========================================
            # 2. TÍNH TOÁN & HIỂN THỊ THANH TIẾN ĐỘ TỔNG
            # ==========================================
            total_tasks = 0
            completed_tasks = 0

            for phase in roadmap_json.get("phases", []):
                for task in phase.get("milestones", []):
                    total_tasks += 1
                    if task.get("status") == "completed":
                        completed_tasks += 1

            progress_percentage = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

            # CSS làm mượt thanh Progress & Gạch ngang chữ
            st.markdown("""
            <style>
            .stProgress > div > div > div > div { background-color: #2E7D32; transition: width 0.5s ease-in-out; }
            .completed-text { text-decoration: line-through; color: #9E9E9E; font-style: italic; transition: all 0.3s; }
            .pending-text { color: #333; font-weight: 500; transition: all 0.3s; }
            div[data-testid="stExpander"] { border-radius: 15px !important; border: 1px solid #E8F5E9 !important; margin-bottom: 10px; }
            </style>
            """, unsafe_allow_html=True)

            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write("") 
                    st.progress(progress_percentage / 100.0)
                with col2:
                    st.markdown(f"<h3 style='color: #2E7D32; text-align: right; margin: 0;'>{progress_percentage}%</h3>", unsafe_allow_html=True)
                    
                if progress_percentage == 100 and total_tasks > 0:
                    st.balloons()
                    st.success("🎉 Xuất sắc! Bạn đã hoàn thành toàn bộ mục tiêu của lộ trình này!")

            st.write("")

            # ==========================================
            # 3. GIAO DIỆN TƯƠNG TÁC (GAMIFICATION)
            # ==========================================
            updated_roadmap = roadmap_json.copy() 
            needs_update = False
            praise_messages = ["Tuyệt vời! 🌟", "Làm tốt lắm! 🔥", "Tiếp tục phát huy nhé! 💪", "Một bước gần hơn tới mục tiêu! 🎯"]

            st.markdown(f"### 🎯 Mục tiêu: **{latest_roadmap.get('target_role', '')}**")

            for p_idx, phase in enumerate(updated_roadmap.get("phases", [])):
                with st.expander(f"🚩 {phase.get('phase_name')}", expanded=True):
                    for t_idx, task in enumerate(phase.get("milestones", [])):
                        is_completed = (task.get("status") == "completed")
                        
                        icon = "✅" if is_completed else "📌"
                        text_class = "completed-text" if is_completed else "pending-text"
                        task_key = f"task_{roadmap_id}_{p_idx}_{t_idx}"
                        task_name = task.get('task', f'Nhiệm vụ {t_idx}')
                        
                        col_check, col_text = st.columns([0.5, 9.5])
                        with col_check:
                            # FIX LỖI STREAMLIT Ở ĐÂY: Truyền task_name vào để không bị rỗng, sau đó ẩn đi
                            new_status = st.checkbox(f"Xong {task_name}", value=is_completed, key=task_key, label_visibility="collapsed")
                            
                        with col_text:
                            st.markdown(f"<span class='{text_class}'>{icon} {task_name} ({task.get('estimated_hours', 0)}h)</span>", unsafe_allow_html=True)

                        if new_status != is_completed:
                            task["status"] = "completed" if new_status else "pending"
                            needs_update = True
                            if new_status: st.toast(random.choice(praise_messages), icon="🎉")

            # Cập nhật Database
            if needs_update:
                with st.spinner("Đang lưu tiến độ..."):
                    db_client.update_data("user_roadmaps", {"id": roadmap_id}, {"roadmap_json": updated_roadmap})
                st.rerun()
                
    with tab_sentiment:
        render_sentiment_dashboard()