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
    """Hàm vẽ Timeline Dọc chuẩn UI/UX"""
    st.info(f"💡 **Chiến lược tổng quan:** {roadmap_data.get('overall_strategy', 'Không có')}")
    
    st.markdown("""
    <style>
    .timeline { position: relative; margin: 20px 0; padding-left: 30px; border-left: 3px solid #C8E6C9; }
    .timeline-item { position: relative; margin-bottom: 30px; }
    .timeline-dot { position: absolute; width: 22px; height: 22px; background: #2E7D32; border-radius: 50%; left: -42.5px; top: 0; border: 4px solid #E8F5E9; box-shadow: 0 0 10px rgba(46,125,50,0.3); }
    .timeline-content { background: rgba(255,255,255,0.8); backdrop-filter: blur(10px); padding: 25px; border-radius: 16px; box-shadow: 0 8px 25px rgba(0,0,0,0.05); border: 1px solid rgba(46,125,50,0.15); transition: transform 0.3s ease; }
    .timeline-content:hover { transform: translateX(8px); border-color: #2E7D32; box-shadow: 5px 8px 30px rgba(46,125,50,0.1); }
    .timeline-title { color: #2E7D32; font-weight: 800; font-size: 1.2em; margin-bottom: 12px; }
    .task-badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold; margin-bottom: 10px; }
    .badge-skill { background: #E3F2FD; color: #1976D2; }
    .badge-cert { background: #FFF3E0; color: #F57C00; }
    .badge-project { background: #F3E5F5; color: #7B1FA2; }
    </style>
    """, unsafe_allow_html=True)

    html_content = '<div class="timeline">'
    for idx, phase in enumerate(roadmap_data.get("phases", [])):
        html_content += f'<div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-content">'
        html_content += f'<div class="timeline-title">📍 Giai đoạn {idx+1}: {phase.get("phase_name", "")}</div>'
        
        for task in phase.get("milestones", []):
            is_done = task.get("status") == "completed"
            
            t_type = task.get("type", "skill")
            badge_class = f"badge-{t_type}"
            icon = "✅" if is_done else ("📘" if t_type == "skill" else "🚀")
            
            text_style = "text-decoration: line-through; color: #9E9E9E;" if is_done else "color: #333;"
            bg_style = "background: #f0f0f0;" if is_done else "background: #fafafa;"

            html_content += f'<div style="margin-bottom: 12px; padding: 10px; {bg_style} border-radius: 10px; border-left: 3px solid {"#2E7D32" if is_done else "#eee"};">'
            html_content += f'<div class="task-badge {badge_class}">{t_type.upper()} {"(Xong)" if is_done else ""}</div>'
            html_content += f'<div style="display: flex; justify-content: space-between; align-items: center; {text_style}">'
            html_content += f'<span>{icon} <b>{task.get("task", "")}</b></span>'
            html_content += '</div></div>'
            
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
    # 1. LỊCH SỬ & QUẢN LÝ DỮ LIỆU
    # ==========================================
    existing_roadmaps = db_client.query_data("user_roadmaps", filters={"user_id": user_id}) or []
    # Sắp xếp từ mới nhất đến cũ nhất
    sorted_roadmaps = sorted(existing_roadmaps, key=lambda x: x.get('created_at', ''), reverse=True)
    latest_roadmap = sorted_roadmaps[0] if sorted_roadmaps else None

    with st.expander("🕒 Lịch sử & Quản lý Lộ trình", expanded=False):
        if sorted_roadmaps:
            st.markdown(f"**Hệ thống đang lưu trữ {len(sorted_roadmaps)} phiên bản lộ trình của bạn:**")
            
            # Duyệt qua từng lộ trình trong lịch sử để tạo list
            for idx, rm in enumerate(sorted_roadmaps):
                with st.container(border=True):
                    c_info, c_del = st.columns([4, 1], vertical_alignment="center")
                    with c_info:
                        # Đánh dấu bản mới nhất cho người dùng dễ nhận biết
                        is_latest_tag = "🌟 **(Đang áp dụng)**" if idx == 0 else "🕒 (Bản lưu trữ)"
                        st.markdown(f"**{rm.get('target_role', 'Chưa rõ mục tiêu')}** {is_latest_tag}")
                        st.caption(f"Thời gian tạo: {rm.get('created_at', 'Không rõ')[:16]} | Khung thời gian: {rm.get('timeframe', '')}")
                    with c_del:
                        # Mỗi lộ trình có một nút Xóa với key độc nhất (dựa vào ID)
                        if st.button("🗑️ Xóa bản này", key=f"del_history_{rm['id']}", type="secondary", use_container_width=True):
                            db_client.delete_data("user_roadmaps", {"id": rm['id']})
                            st.toast("Đã dọn dẹp lộ trình cũ!", icon="✅")
                            import time
                            time.sleep(1)
                            st.rerun()
        else:
            st.info("💡 Bạn chưa tạo lộ trình nào.")

    st.divider()

    # 2. GIAO DIỆN CHÍNH
    with st.container(border=True):
        tab_view, tab_create = st.tabs(["🗺️ Lộ trình của tôi", "✨ AI Thiết kế Lộ trình mới"])

        with tab_view:
            if latest_roadmap:
                st.markdown(f"<h3 style='text-align: center; color: #1976D2;'>Mục tiêu: {latest_roadmap['target_role']} ({latest_roadmap['timeframe']})</h3>", unsafe_allow_html=True)
                try:
                    roadmap_json = latest_roadmap['roadmap_json']
                    if isinstance(roadmap_json, str):
                        roadmap_json = json.loads(roadmap_json)
                    render_timeline_ui(roadmap_json)
                except Exception as e:
                    st.error(f"Dữ liệu lộ trình bị lỗi: {e}")
            else:
                st.info("Chưa có dữ liệu. Hãy chuyển sang tab tạo mới!")

        with tab_create:
            with st.form("roadmap_generator_form"):
                st.markdown("### 🎯 Khai báo Mục tiêu")
                col1, col2 = st.columns(2)
                with col1:
                    target_role = st.text_input("Vị trí hướng tới (VD: Data Scientist, Manager)")
                with col2:
                    timeframe = st.selectbox("Khung thời gian", ["6 Tháng", "1 Năm", "2 Năm", "3 Năm+"])
                
                st.markdown("---")
                st.caption("💡 Tùy chọn cách AI xây dựng lộ trình cho bạn:")
                
                # TẠO 2 NÚT SUBMIT SONG SONG
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    submit_pivot = st.form_submit_button("🔄 Kế thừa tiến độ (Chuyển nhánh)", type="primary")
                with btn_col2:
                    submit_new = st.form_submit_button("✨ Xây lại từ đầu", type="secondary")

            # XỬ LÝ KHI NGƯỜI DÙNG BẤM 1 TRONG 2 NÚT
            if (submit_pivot or submit_new) and target_role:
                keep_progress = submit_pivot # True nếu chọn Kế thừa
                
                done_skills = []
                if keep_progress and latest_roadmap:
                    old_json = latest_roadmap['roadmap_json']
                    if isinstance(old_json, str):
                        try: old_json = json.loads(old_json)
                        except: old_json = {}
                        
                    for p in old_json.get("phases", []):
                        for m in p.get("milestones", []):
                            if m.get("status") == "completed":
                                done_skills.append(m.get("task"))

                with st.spinner("🔄 Đang phân tích dữ liệu..."):
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

                with st.spinner("🧠 AI đang tính toán lộ trình..."):
                    skills_context = f"DỮ LIỆU ĐÃ CÓ: Người dùng ĐÃ THÀNH THẠO các kỹ năng: {', '.join(done_skills)}. KHÔNG bắt học lại các phần này, hãy dùng nó làm nền tảng đầu tiên." if done_skills else ""
                    
                    system_prompt = f"""Bạn là MAPLIFE AI, Kiến trúc sư Sự nghiệp.
                    CV: {latest_cv[:500] if latest_cv else 'Trống'}
                    Tính cách: {latest_test if latest_test else 'Trống'}
                    MỤC TIÊU: {target_role} | THỜI GIAN: {timeframe}
                    {skills_context}

                    Trả về DUY NHẤT 1 JSON:
                    {{
                      "target_role": "{target_role}", "timeframe": "{timeframe}", "overall_strategy": "...",
                      "phases": [ {{ "phase_name": "...", "milestones": [ {{"task": "...", "status": "pending", "type": "skill", "estimated_hours": 50}} ] }} ]
                    }}
                    """
                    try:
                        raw_response = ai_client.generate_response([{"role": "system", "content": system_prompt}], max_tokens=5000)
                        roadmap_data = json.loads(clean_json_string(raw_response))
                        
                        # Nhồi lại các kỹ năng đã có vào Phase đầu tiên để đồng bộ UI
                        if keep_progress and done_skills:
                            inherited_phase = {"phase_name": "Nền tảng đã tích lũy", "milestones": []}
                            for skill in done_skills:
                                inherited_phase["milestones"].append({"task": skill, "status": "completed", "type": "skill"})
                            roadmap_data["phases"].insert(0, inherited_phase)

                        db_client.insert_data("user_roadmaps", {"user_id": user_id, "target_role": target_role, "timeframe": timeframe, "roadmap_json": roadmap_data})
                        st.success("🎉 Tạo lộ trình thành công!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error("AI đang quá tải, vui lòng thử lại!")