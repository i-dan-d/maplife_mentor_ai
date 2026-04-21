import streamlit as st
import json
from core.openai_client import OpenAIClient
from core.supabase_client import SupabaseClient

def clean_json_string(raw_text):
    """Hàm dọn dẹp phòng trường hợp AI trả về thẻ markdown ```json"""
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

def render_roadmap_ui(roadmap_data):
    """Hàm vẽ JSON thành giao diện Timeline đẹp mắt"""
    st.info(f"💡 Chiến lược: {roadmap_data.get('overall_strategy', 'Không có')}")
    
    phases = roadmap_data.get("phases", [])
    for idx, phase in enumerate(phases):
        with st.expander(f"🚩 {phase.get('phase_name', f'Giai đoạn {idx+1}')}", expanded=(idx==0)):
            for task in phase.get("milestones", []):
                # Phân loại màu sắc/icon theo type
                task_type = task.get("type", "skill")
                if task_type == "skill": icon = "📘"
                elif task_type == "cert": icon = "📜"
                elif task_type == "project": icon = "🚀"
                else: icon = "📌"
                
                hours = task.get("estimated_hours", 0)
                hour_text = f"({hours}h)" if hours else ""
                
                # Hiển thị task dạng checkbox vô hiệu hóa (chỉ để xem)
                st.checkbox(f"{icon} **{task.get('task', '')}** {hour_text}", value=(task.get("status") == "completed"), disabled=True)

def roadmap():
    st.header("🛤️ Xây dựng Lộ trình Sự nghiệp")
    
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Vui lòng đăng nhập để sử dụng tính năng này.")
        return

    db_client = SupabaseClient()
    ai_client = OpenAIClient()

    tab_view, tab_create = st.tabs(["🗺️ Lộ trình của tôi", "✨ Tạo lộ trình mới"])

    # --- TAB 1: XEM LỘ TRÌNH ĐÃ TẠO ---
    with tab_view:
        existing_roadmaps = db_client.query_data("user_roadmaps", filters={"user_id": user_id}) or []
        if existing_roadmaps:
            # Lấy lộ trình mới nhất
            latest_roadmap = sorted(existing_roadmaps, key=lambda x: x['created_at'], reverse=True)[0]
            st.success(f"🎯 Mục tiêu: **{latest_roadmap['target_role']}** | ⏳ Thời gian: **{latest_roadmap['timeframe']}**")
            
            try:
                # Đảm bảo parse JSON an toàn
                roadmap_json = latest_roadmap['roadmap_json']
                if isinstance(roadmap_json, str):
                    roadmap_json = json.loads(roadmap_json)
                render_roadmap_ui(roadmap_json)
            except Exception as e:
                st.error("Dữ liệu lộ trình bị lỗi định dạng.")
        else:
            st.info("Bạn chưa có lộ trình nào. Hãy chuyển sang tab 'Tạo lộ trình mới' nhé!")

    # --- TAB 2: TẠO LỘ TRÌNH MỚI BẰNG AI ---
    with tab_create:
        with st.form("roadmap_generator_form"):
            st.subheader("Khai báo Mục tiêu")
            col1, col2 = st.columns(2)
            with col1:
                target_role = st.text_input("Vị trí hướng tới (VD: Senior Data Analyst, Project Manager)")
            with col2:
                timeframe = st.selectbox("Khung thời gian dự kiến", ["6 Tháng", "1 Năm", "2 Năm", "3 Năm+"])
            
            submit_btn = st.form_submit_button("🚀 Phân tích & Sinh Lộ trình", type="primary")

        if submit_btn and target_role:
            with st.spinner("Đang thu thập hồ sơ cá nhân..."):
                # 1. Thu thập Context (CV & Tính cách)
                all_docs = db_client.query_data("documents", select_query="id, content, metadata") or []
                latest_cv, latest_test = "", ""
                for doc in all_docs:
                    meta = doc.get("metadata", {})
                    if isinstance(meta, str):
                        try: meta = json.loads(meta)
                        except: pass
                    
                    if str(meta.get("user_id")) == str(user_id):
                        if meta.get("source") in ["pdf_upload", "manual_form"]:
                            latest_cv = doc.get('content')
                        elif meta.get("source") == "personality_test":
                            latest_test = doc.get('content')

            with st.spinner("AI đang tính toán khoảng cách kỹ năng và lập kế hoạch... (Khoảng 10-15s)"):
                # 2. Xây dựng Prompt "Ép" JSON
                system_prompt = f"""Bạn là MAPLIFE AI, Kiến trúc sư Lộ trình Sự nghiệp.
                Dưới đây là thông tin người dùng:
                <USER_PROFILE>
                <CV>{latest_cv if latest_cv else 'Trống'}</CV>
                <PERSONALITY>{latest_test if latest_test else 'Trống'}</PERSONALITY>
                </USER_PROFILE>

                MỤC TIÊU: {target_role} | THỜI GIAN: {timeframe}

                LỆNH TỐI CAO: BẮT BUỘC chỉ trả về 1 đối tượng JSON duy nhất theo đúng cấu trúc dưới đây. KHÔNG giải thích, KHÔNG chào hỏi, KHÔNG bọc thẻ markdown.
                {{
                  "target_role": "{target_role}",
                  "timeframe": "{timeframe}",
                  "overall_strategy": "Câu tóm tắt chiến lược...",
                  "phases": [
                    {{
                      "phase_name": "Tên giai đoạn 1...",
                      "milestones": [
                        {{"task": "Tên công việc", "status": "pending", "type": "skill", "estimated_hours": 50}}
                      ]
                    }}
                  ]
                }}
                Chú ý: 'type' chỉ được chọn 1 trong: skill, cert, project, knowledge.
                """

                # 3. Gọi AI
                raw_response = ai_client.generate_response([{"role": "system", "content": system_prompt}], max_tokens=5000)
                
                try:
                    # 4. Làm sạch và Parse JSON
                    clean_str = clean_json_string(raw_response)
                    roadmap_data = json.loads(clean_str)
                    
                    # 5. Lưu Database
                    db_client.insert_data("user_roadmaps", {
                        "user_id": user_id,
                        "target_role": target_role,
                        "timeframe": timeframe,
                        "roadmap_json": roadmap_data
                    })
                    
                    st.success("Tạo lộ trình thành công! Dữ liệu đã được lưu lại.")
                    st.balloons()
                    # Tự động tải lại trang để hiển thị bên Tab "Lộ trình của tôi"
                    st.rerun()
                    
                except json.JSONDecodeError as e:
                    st.error("AI trả về định dạng không hợp lệ. Vui lòng thử lại!")
                    st.code(raw_response) # In ra để debug nếu lỗi