import streamlit as st
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

def personality_test():
    st.header("🧪 Hồ sơ Tâm lý & Phong cách làm việc")
    
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Vui lòng đăng nhập để thực hiện bài test.")
        return

    db_client = SupabaseClient()

    st.markdown("Để AI Mentor có thể đưa ra lộ trình chính xác nhất, hãy hoàn thành 2 bài tự đánh giá dưới đây. Quá trình này chỉ mất khoảng 2 phút!")

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
            bf_o = st.slider("Sẵn sàng trải nghiệm (O)", 0, 100, 50, help="Điểm cao: Thích cái mới, rủi ro. Điểm thấp: Thích sự quen thuộc, an toàn.")
            bf_c = st.slider("Sự Kỷ luật/Tận tâm (C)", 0, 100, 50, help="Điểm cao: Có tổ chức, chi tiết. Điểm thấp: Linh hoạt, ngẫu hứng.")
            bf_e = st.slider("Sự Hướng ngoại (E)", 0, 100, 50, help="Điểm cao: Thích nói chuyện, năng động. Điểm thấp: Yên tĩnh, tập trung.")
        with col4:
            bf_a = st.slider("Sự Hòa đồng (A)", 0, 100, 50, help="Điểm cao: Đề cao tập thể, nhường nhịn. Điểm thấp: Thẳng thắn, phản biện.")
            bf_n = st.slider("Sự Nhạy cảm/Áp lực (N)", 0, 100, 50, help="Điểm cao: Hay lo âu, nhạy cảm. Điểm thấp: Điềm tĩnh, thần kinh thép.")

        submit_btn = st.form_submit_button("Lưu Hồ Sơ Tâm Lý", type="primary")

        if submit_btn:
            with st.spinner("Đang biên dịch hồ sơ để nạp vào não AI..."):
                # 1. Tính toán mã Holland (Top 3)
                holland_scores = {'R': h_r, 'I': h_i, 'A': h_a, 'S': h_s, 'E': h_e, 'C': h_c}
                top_3_holland = sorted(holland_scores.items(), key=lambda x: x[1], reverse=True)[:3]
                holland_code = "".join([item[0] for item in top_3_holland])
                
                # 2. Sinh báo cáo Big Five
                work_style_report = interpret_big_five(bf_o, bf_c, bf_e, bf_a, bf_n)

                # 3. Đóng gói thành XML Text để AI đọc hiểu dễ nhất
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

                # 4. Lưu hoặc Cập nhật vào bảng documents
                # Kiểm tra xem user đã có bài test nào chưa để update, nếu chưa thì insert
                existing_docs = db_client.query_data("documents", filters={"metadata->>user_id": user_id, "metadata->>source": "personality_test"}) or []
                
                if existing_docs:
                    # Update
                    doc_id = existing_docs[0]['id']
                    db_client.update_data(
                        table_name="documents",
                        match_conditions={"id": doc_id},
                        update_data={"content": ai_readable_profile}
                    )
                else:
                    # Insert mới
                    db_client.insert_data("documents", {
                        "content": ai_readable_profile,
                        "metadata": {"user_id": user_id, "source": "personality_test"}
                    })

                st.success(f"🎉 Lưu thành công! Mã nghề nghiệp của bạn là: **{holland_code}**")
                st.info("Bây giờ bạn có thể sang tab 'AI Mentor Chat' hoặc 'Lộ trình sự nghiệp' để xem AI tư vấn dựa trên tính cách này nhé!")