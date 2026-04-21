import streamlit as st
import json
from core.supabase_client import SupabaseClient

def progress_tracker():
    st.header("📊 Theo dõi Tiến độ (Progress Tracker)")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Vui lòng đăng nhập để xem tiến độ của bạn.")
        return

    db_client = SupabaseClient()

    # ==========================================
    # 1. TRUY XUẤT LỘ TRÌNH MỚI NHẤT
    # ==========================================
    existing_roadmaps = db_client.query_data("user_roadmaps", filters={"user_id": user_id}) or []
    if not existing_roadmaps:
        st.info("💡 Bạn chưa có lộ trình nào để theo dõi. Hãy sang tab 'Lộ trình sự nghiệp' để tạo nhé!")
        return

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

    # Tính phần trăm (tránh lỗi chia cho 0)
    progress_percentage = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(progress_percentage / 100.0)
    with col2:
        st.subheader(f"{progress_percentage}% Hoàn thành")
        
    if progress_percentage == 100:
        st.balloons()
        st.success("🎉 Xuất sắc! Bạn đã hoàn thành toàn bộ lộ trình này!")

    st.divider()

    # ==========================================
    # 3. GIAO DIỆN TƯƠNG TÁC (MỞ KHÓA CHECKBOX)
    # ==========================================
    updated_roadmap = roadmap_json.copy() # Tạo bản sao để sửa đổi
    needs_update = False

    st.markdown(f"### 🎯 Mục tiêu: **{latest_roadmap.get('target_role', '')}**")
    
    for p_idx, phase in enumerate(updated_roadmap.get("phases", [])):
        st.markdown(f"#### 🚩 {phase.get('phase_name')}")
        
        for t_idx, task in enumerate(phase.get("milestones", [])):
            is_completed = (task.get("status") == "completed")
            
            # Icon trang trí
            task_type = task.get("type", "skill")
            icon = "📘" if task_type == "skill" else "📜" if task_type == "cert" else "🚀" if task_type == "project" else "📌"
            
            # Tạo key ĐỘC NHẤT cho mỗi checkbox để Streamlit không bị nhầm lẫn
            task_key = f"task_{roadmap_id}_{p_idx}_{t_idx}"
            
            # ĐÂY CHÍNH LÀ CHECKBOX "SỐNG" (Không có disabled=True)
            new_status = st.checkbox(
                f"{icon} {task.get('task', '')} ({task.get('estimated_hours', 0)}h)", 
                value=is_completed, 
                key=task_key
            )

            # ==========================================
            # 4. BẮT SỰ KIỆN CLICK & LƯU DATABASE
            # ==========================================
            if new_status != is_completed:
                task["status"] = "completed" if new_status else "pending"
                needs_update = True

    # Cập nhật một lần duy nhất xuống Database nếu có thay đổi
    if needs_update:
        with st.spinner("Đang lưu tiến độ..."):
            db_client.update_data(
                table_name="user_roadmaps",
                match_conditions={"id": roadmap_id},
                update_data={"roadmap_json": updated_roadmap} # Lưu lại toàn bộ khối JSON mới
            )
        st.toast("Đã lưu tiến độ!", icon="💾")
        st.rerun() # Tải lại trang ngay lập tức để thanh Progress Bar chạy lên