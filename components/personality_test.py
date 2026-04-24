import streamlit as st
import plotly.graph_objects as go
import json
from core.supabase_client import SupabaseClient

def interpret_big_five(o, c, e, a, n):
    """Hàm tạo báo cáo phong cách làm việc dựa trên điểm Big Five"""
    report = []
    # O - Openness
    if o > 70: report.append("- Tư duy: Rất sáng tạo, thích cái mới, phù hợp môi trường đổi mới liên tục (R&D, Design).")
    elif o < 40: report.append("- Tư duy: Thực tế, thích làm việc theo quy trình rõ ràng, có tính hệ thống cao.")
    
    # C - Conscientiousness
    if c > 70: report.append("- Kỷ luật: Cực kỳ tận tâm, làm việc có kế hoạch, tỉ mỉ. Phù hợp làm Quản lý/Leader.")
    elif c < 40: report.append("- Kỷ luật: Linh hoạt, thích ứng nhanh, đôi khi làm việc theo ngẫu hứng.")
    
    # E - Extraversion
    if e > 70: report.append("- Giao tiếp: Hướng ngoại, thích đám đông, giỏi thuyết phục và truyền năng lượng.")
    elif e < 40: report.append("- Giao tiếp: Hướng nội, thích tập trung sâu, làm việc độc lập hoặc nhóm nhỏ.")
    
    # A - Agreeableness
    if a > 70: report.append("- Làm việc nhóm: Hòa đồng, dĩ hòa vi quý, luôn nghĩ cho lợi ích tập thể.")
    elif a < 40: report.append("- Làm việc nhóm: Thẳng thắn, phản biện mạnh mẽ, không ngại va chạm để bảo vệ ý kiến.")
    
    # N - Neuroticism
    if n > 70: report.append("- Chịu áp lực: Khá nhạy cảm, dễ căng thẳng. Cần môi trường làm việc ổn định, rõ ràng.")
    elif n < 40: report.append("- Chịu áp lực: Thần kinh thép, giữ bình tĩnh cực tốt trong khủng hoảng và deadline.")
    
    return "\n".join(report)

def create_radar_chart(categories, scores, title, line_color, fill_color):
    """Hàm phụ trợ vẽ biểu đồ Radar Plotly để tái sử dụng cho nhiều mô hình"""
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]], # Khép kín vòng
        theta=categories + [categories[0]],
        fill='toself', 
        fillcolor=fill_color,
        line=dict(color=line_color, width=2),
        name=title,
        marker=dict(size=6, color=line_color)
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, gridcolor="rgba(0,0,0,0.1)"),
            angularaxis=dict(tickfont=dict(size=12, color="#1F2937"))
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=20),
        height=320,
        title=dict(text=title, font=dict(size=16, color=line_color, family="sans serif"), x=0.5)
    )
    return fig

def personality_test():
    st.header("🧪 Hồ sơ Tâm lý & Phong cách làm việc")
    
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Vui lòng đăng nhập để thực hiện bài test.")
        return

    db_client = SupabaseClient()

    st.markdown("Để AI Mentor có thể đưa ra lộ trình chính xác nhất, hãy hoàn thành 2 bài tự đánh giá dưới đây. Quá trình này chỉ mất khoảng 2 phút!")

    # Bọc Form vào Custom Card để đồng bộ UI Glassmorphism
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)

    with st.form("personality_assessment_form"):
        # --- PHẦN 1: MÔ HÌNH HOLLAND ---
        st.subheader("Phần 1: Định hướng Nghề nghiệp (Holland - RIASEC)")
        st.caption("Chấm điểm từ 0-100 mức độ yêu thích/phù hợp của bạn với các nhóm sau:")
        
        col1, col2 = st.columns(2)
        with col1:
            h_r = st.slider("Kỹ thuật/Thực tế (R)", 0, 100, 50, help="Thích làm việc với máy móc, công cụ, hiện vật.")
            h_i = st.slider("Nghiên cứu/Phân tích (I)", 0, 100, 50, help="Thích toán học, khoa học, phân tích dữ liệu.")
            h_a = st.slider("Nghệ thuật/Sáng tạo (A)", 0, 100, 50, help="Thích thiết kế, viết lách, sáng tạo không khuôn mẫu.")
        with col2:
            h_s = st.slider("Xã hội/Giúp đỡ (S)", 0, 100, 50, help="Thích tư vấn, giảng dạy, hỗ trợ người khác.")
            h_e = st.slider("Quản lý/Thuyết phục (E)", 0, 100, 50, help="Thích lãnh đạo, kinh doanh, dẫn dắt đội nhóm.")
            h_c = st.slider("Tổ chức/Quy tắc (C)", 0, 100, 50, help="Thích làm việc với con số, giấy tờ, quy trình chặt chẽ.")

        st.divider()

        # --- PHẦN 2: MÔ HÌNH BIG FIVE ---
        st.subheader("Phần 2: Phong cách Làm việc (Big Five - OCEAN)")
        st.caption("Chấm điểm từ 0-100 để phản ánh đúng nhất tính cách tự nhiên của bạn:")
        
        col3, col4 = st.columns(2)
        with col3:
            bf_o = st.slider("Sẵn sàng trải nghiệm (O)", 0, 100, 50)
            bf_c = st.slider("Sự Kỷ luật/Tận tâm (C)", 0, 100, 50)
            bf_e = st.slider("Sự Hướng ngoại (E)", 0, 100, 50)
        with col4:
            bf_a = st.slider("Sự Hòa đồng (A)", 0, 100, 50)
            bf_n = st.slider("Sự Nhạy cảm/Áp lực (N)", 0, 100, 50)

        submit_btn = st.form_submit_button("Lưu & Phân tích Hồ sơ", type="primary")

    st.markdown('</div>', unsafe_allow_html=True)

    # --- XỬ LÝ VÀ VẼ BIỂU ĐỒ SAU KHI SUBMIT ---
    if submit_btn:
        with st.spinner("Đang vẽ bản đồ tính cách và lưu vào não bộ AI..."):
            # 1. Tính toán mã Holland
            holland_scores = {'R': h_r, 'I': h_i, 'A': h_a, 'S': h_s, 'E': h_e, 'C': h_c}
            top_3_holland = sorted(holland_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            holland_code = "".join([item[0] for item in top_3_holland])
            
            # 2. Sinh báo cáo Big Five
            work_style_report = interpret_big_five(bf_o, bf_c, bf_e, bf_a, bf_n)

            # 3. Đóng gói thành XML Text (Logic cũ của cậu rất chuẩn)
            ai_readable_profile = f"""
            <HOLLAND_PROFILE>
            - Điểm số: {holland_scores}
            - Mã nổi trội (Top 3): {holland_code}
            - Đánh giá: Người dùng phù hợp với các công việc mang đặc tính của nhóm {holland_code}.
            </HOLLAND_PROFILE>

            <BIG_FIVE_PROFILE>
            - Điểm số: O:{bf_o}, C:{bf_c}, E:{bf_e}, A:{bf_a}, N:{bf_n}
            - Phong cách làm việc chi tiết:
            {work_style_report}
            </BIG_FIVE_PROFILE>
            """.strip()

            # 4. Lưu DB
            existing_docs = db_client.query_data("documents", filters={"metadata->>user_id": user_id, "metadata->>source": "personality_test"}) or []
            if existing_docs:
                db_client.update_data("documents", {"id": existing_docs[0]['id']}, {"content": ai_readable_profile})
            else:
                db_client.insert_data("documents", {"content": ai_readable_profile, "metadata": {"user_id": user_id, "source": "personality_test"}})

            # 5. HIỂN THỊ KẾT QUẢ TRỰC QUAN (DUAL RADAR CHARTS)
            st.success(f"🎉 Lưu thành công! Mã nghề nghiệp của bạn là: **{holland_code}**")
            
            # Vẽ 2 biểu đồ cạnh nhau
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                h_categories = ['Kỹ thuật (R)', 'Nghiên cứu (I)', 'Nghệ thuật (A)', 'Xã hội (S)', 'Quản lý (E)', 'Nghiệp vụ (C)']
                h_scores_list = [h_r, h_i, h_a, h_s, h_e, h_c]
                # Biểu đồ Holland dùng màu Xanh lá chủ đạo của MAPLIFE
                fig_holland = create_radar_chart(h_categories, h_scores_list, "Lưới nghề nghiệp (RIASEC)", "#2E7D32", "rgba(46, 125, 50, 0.3)")
                st.plotly_chart(fig_holland, use_container_width=True)

            with chart_col2:
                bf_categories = ['Trải nghiệm (O)', 'Kỷ luật (C)', 'Hướng ngoại (E)', 'Hòa đồng (A)', 'Áp lực (N)']
                bf_scores_list = [bf_o, bf_c, bf_e, bf_a, bf_n]
                # Biểu đồ Big Five dùng màu Xanh dương nhạt cho khác biệt
                fig_bf = create_radar_chart(bf_categories, bf_scores_list, "Phong cách làm việc (OCEAN)", "#1976D2", "rgba(25, 118, 210, 0.3)")
                st.plotly_chart(fig_bf, use_container_width=True)

            # In thêm cái báo cáo chi tiết cậu đã làm
            with st.expander("📄 Xem giải nghĩa chi tiết phong cách làm việc của bạn"):
                st.markdown(work_style_report)