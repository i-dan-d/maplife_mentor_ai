import streamlit as st
import json
import time
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

def render_timeline_ui(roadmap_data):
    """Hàm vẽ Timeline Dọc (Vertical Timeline) bằng HTML/CSS"""
    st.info(f"💡 **Chiến lược tổng quan:** {roadmap_data.get('overall_strategy', 'Không có')}")
    
    # Inject CSS tùy chỉnh cho Timeline
    st.markdown("""
    <style>
    .timeline { position: relative; margin: 20px 0; padding-left: 30px; border-left: 3px solid #C8E6C9; }
    .timeline-item { position: relative; margin-bottom: 30px; }
    .timeline-dot { position: absolute; width: 22px; height: 22px; background: #2E7D32; border-radius: 50%; left: -42.5px; top: 0; border: 4px solid #E8F5E9; box-shadow: 0 0 10px rgba(46,125,50,0.3); }
    .timeline-content { background: rgba(255,255,255,0.8); backdrop-filter: blur(10px); padding: 25px; border-radius: 16px; box-shadow: 0 8px 25px rgba(0,0,0,0.05); border: 1px solid rgba(46,125,50,0.15); transition: transform 0.3s ease; }
    .timeline-content:hover { transform: translateX(5px); border-color: #2E7D32; }
    .timeline-title { color: #2E7D32; font-weight: 800; font-size: 1.2em; margin-bottom: 15px; border-bottom: 1px dashed #C8E6C9; padding-bottom: 10px; }
    .task-item { display: flex; align-items: flex-start; margin-bottom: 12px; padding: 12px; background: #fdfdfd; border-radius: 12px; border: 1px solid #f0f0f0; }
    .task-icon { margin-right: 15px; font-size: 1.4em; }
    .task-text { flex-grow: 1; color: #333; font-size: 0.95em; line-height: 1.4; }
    .task-time { color: #2E7D32; font-size: 0.85em; font-weight: bold; background: #E8F5E9; padding: 4px 10px; border-radius: 20px; white-space: nowrap; margin-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

    # VIẾT HTML TRÊN 1 DÒNG HOẶC KHÔNG THỤT LỀ ĐỂ TRÁNH LỖI MARKDOWN
    html_content = '<div class="timeline">'
    for idx, phase in enumerate(roadmap_data.get("phases", [])):
        html_content += f'<div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-content">'
        html_content += f'<div class="timeline-title">📍 Giai đoạn {idx+1}: {phase.get("phase_name", "")}</div>'
        
        for task in phase.get("milestones", []):
            t_type = task.get("type", "skill")
            if t_type == "skill": icon = "📘"
            elif t_type == "cert": icon = "📜"
            elif t_type == "project": icon = "🚀"
            else: icon = "📌"
            
            hours = task.get("estimated_hours", 0)
            hour_badge = f'<span class="task-time">⏳ {hours}h</span>' if hours else ''
            
            # Khối HTML này phải viết liền để không dính khoảng trắng thụt lề
            html_content += f'<div class="task-item"><span class="task-icon">{icon}</span><span class="task-text"><b>{task.get("task", "")}</b></span>{hour_badge}</div>'
            
        html_content += '</div></div>'
    html_content += '</div>'

    st.markdown(html_content, unsafe_allow_html=True)

def roadmap():
    st.markdown("<h2 style='text-align: center; color: #2E7D32;'>🛤️ Xây dựng Lộ trình Sự nghiệp</h2>", unsafe_allow_html=True)
    
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Vui lòng đăng nhập để sử dụng tính năng này.")
        return

    db_client = SupabaseClient()
    ai_client = OpenAIClient()

    # ==========================================
    # 1. QUẢN LÝ DỮ LIỆU & MINH BẠCH
    # ==========================================
    existing_roadmaps = db_client.query_data("user_roadmaps", filters={"user_id": user_id}) or []
    latest_roadmap = sorted(existing_roadmaps, key=lambda x: x['created_at'], reverse=True)[0] if existing_roadmaps else None

    with st.expander("🛡️ Quản lý & Kiểm soát Dữ liệu Lộ trình", expanded=(not latest_roadmap)):
        if latest_roadmap:
            st.success(f"✅ Hệ thống đang lưu trữ {len(existing_roadmaps)} phiên bản lộ trình của bạn.")
            col_info, col_action = st.columns([3, 1])
            with col_info:
                st.caption(f"Lộ trình hiện tại: **{latest_roadmap['target_role']}** | Cập nhật: {latest_roadmap['created_at']}")
                if st.checkbox("Xem dữ liệu JSON gốc đang lưu"):
                    st.json(latest_roadmap['roadmap_json'])
            with col_action:
                if st.button("🗑️ Xóa dữ liệu", type="secondary", use_container_width=True):
                    # Xóa tất cả lộ trình của user này để làm sạch
                    for rm in existing_roadmaps:
                        db_client.delete_data("user_roadmaps", {"id": rm['id']})
                    st.success("Đã xóa sạch lộ trình khỏi hệ thống!")
                    time.sleep(1)
                    st.rerun()
        else:
            st.info("💡 Bạn chưa có lộ trình nào. Dữ liệu lộ trình tạo ra sẽ được lưu trữ dưới định dạng JSON minh bạch tại đây.")

    st.divider()

    # ==========================================
    # 2. GIAO DIỆN CHÍNH (TABS)
    # ==========================================
    with st.container(border=True):
        tab_view, tab_create = st.tabs(["🗺️ Lộ trình của tôi", "✨ AI Thiết kế Lộ trình mới"])

        # --- TAB 1: HIỂN THỊ TIMELINE ---
        with tab_view:
            if latest_roadmap:
                st.markdown(f"<h3 style='text-align: center; color: #1976D2;'>Mục tiêu: {latest_roadmap['target_role']} ({latest_roadmap['timeframe']})</h3>", unsafe_allow_html=True)
                try:
                    roadmap_json = latest_roadmap['roadmap_json']
                    if isinstance(roadmap_json, str):
                        roadmap_json = json.loads(roadmap_json)
                    # Gọi hàm vẽ HTML Timeline
                    render_timeline_ui(roadmap_json)
                except Exception as e:
                    st.error(f"Dữ liệu lộ trình bị lỗi định dạng: {e}")
            else:
                st.info("Chưa có dữ liệu. Hãy chuyển sang tab 'AI Thiết kế' để bắt đầu!")

        # --- TAB 2: TẠO LỘ TRÌNH MỚI BẰNG AI ---
        with tab_create:
            with st.form("roadmap_generator_form"):
                st.markdown("### 🎯 Khai báo Mục tiêu")
                col1, col2 = st.columns(2)
                with col1:
                    target_role = st.text_input("Vị trí hướng tới (VD: Data Scientist, HR Manager)")
                with col2:
                    timeframe = st.selectbox("Khung thời gian dự kiến", ["6 Tháng", "1 Năm", "2 Năm", "3 Năm+"])
                
                submit_btn = st.form_submit_button("🚀 Yêu cầu MAPLIFE phân tích & Lập kế hoạch", type="primary")

            if submit_btn and target_role:
                with st.spinner("🔄 Đang nạp Hồ sơ CV và Tính cách từ Database..."):
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

                with st.spinner("🧠 AI đang tính toán lộ trình tối ưu nhất cho bạn (Khoảng 10-15s)..."):
                    system_prompt = f"""Bạn là MAPLIFE AI, Kiến trúc sư Lộ trình Sự nghiệp.
                    Hồ sơ người dùng hiện tại:
                    <USER_PROFILE>
                    <CV>{latest_cv if latest_cv else 'Trống'}</CV>
                    <PERSONALITY>{latest_test if latest_test else 'Trống'}</PERSONALITY>
                    </USER_PROFILE>

                    MỤC TIÊU: {target_role} | THỜI GIAN: {timeframe}

                    LỆNH TỐI CAO: BẮT BUỘC trả về 1 đối tượng JSON duy nhất. Không giải thích thêm.
                    {{
                      "target_role": "{target_role}",
                      "timeframe": "{timeframe}",
                      "overall_strategy": "Câu tóm tắt chiến lược...",
                      "phases": [
                        {{
                          "phase_name": "Tên giai đoạn 1",
                          "milestones": [
                            {{"task": "Tên công việc", "status": "pending", "type": "skill", "estimated_hours": 50}}
                          ]
                        }}
                      ]
                    }}
                    Loại task (type) chỉ được chọn: skill, cert, project, knowledge.
                    """

                    try:
                        raw_response = ai_client.generate_response([{"role": "system", "content": system_prompt}], max_tokens=5000)
                        clean_str = clean_json_string(raw_response)
                        roadmap_data = json.loads(clean_str)
                        
                        # LƯU VÀO DATABASE
                        db_client.insert_data("user_roadmaps", {
                            "user_id": user_id,
                            "target_role": target_role,
                            "timeframe": timeframe,
                            "roadmap_json": roadmap_data
                        })
                        
                        st.success("🎉 Tạo lộ trình thành công! Đang chuyển hướng...")
                        time.sleep(1)
                        st.rerun()
                        
                    except Exception as e:
                        st.error("AI đang quá tải hoặc cấu trúc trả về bị lệch. Vui lòng thử lại!")
                        st.code(str(e))