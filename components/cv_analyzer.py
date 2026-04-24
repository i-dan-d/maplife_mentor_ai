import streamlit as st
import PyPDF2
import json
import plotly.graph_objects as go
from core.openai_client import OpenAIClient
from core.supabase_client import SupabaseClient
import time

def extract_text_from_pdf(file):
    """Trích xuất văn bản từ file PDF"""
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted: text += extracted + "\n"
    return text

def create_donut_chart(score, label):
    """Vẽ biểu đồ Donut chấm điểm CV"""
    # Đổi màu tùy theo điểm số
    color = '#2E7D32' if score >= 75 else '#F57C00' if score >= 50 else '#D32F2F'
    fig = go.Figure(go.Pie(
        values=[score, 100 - score],
        labels=[label, "Cần tối ưu"],
        hole=.75,
        marker_colors=[color, 'rgba(0,0,0,0.05)'],
        textinfo='none'
    ))
    fig.update_layout(
        annotations=[dict(text=f'{score}', x=0.5, y=0.5, font_size=45, font_family="Arial Black", showarrow=False, font_color=color)],
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=220,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def cv_analyzer():
    st.markdown("<h2 style='text-align: center; color: #2E7D32;'>📄 Phân tích & Tối ưu CV</h2>", unsafe_allow_html=True)
    
    ai_client = OpenAIClient()
    db_client = SupabaseClient()
    user_id = st.session_state.get("user_id")

    if not user_id:
        st.warning("Vui lòng đăng nhập để quản lý và phân tích hồ sơ.")
        return

    # ==========================================
    # 1. TRUY XUẤT VÀ QUẢN LÝ DỮ LIỆU (MINH BẠCH)
    # ==========================================
    all_docs = db_client.query_data("documents", filters={"metadata->>user_id": user_id}) or []
    
    # Lọc ra tài liệu CV (Raw Text) và Phân tích JSON
    cv_raw_docs = [doc for doc in all_docs if doc.get('metadata', {}).get('type') == 'personal_profile']
    cv_analysis_docs = [doc for doc in all_docs if doc.get('metadata', {}).get('type') == 'cv_analysis_result']

    latest_raw_cv = cv_raw_docs[-1] if cv_raw_docs else None
    latest_analysis = cv_analysis_docs[-1] if cv_analysis_docs else None

    with st.expander("🛡️ Quản lý & Kiểm soát Dữ liệu Hồ sơ", expanded=(not latest_raw_cv)):
        if latest_raw_cv:
            st.success("✅ Hồ sơ của bạn đã được mã hóa (Embedding) và lưu an toàn trong não bộ AI.")
            col_info, col_action = st.columns([3, 1])
            with col_info:
                st.caption(f"Trạng thái: **Đang sử dụng** | Cập nhật lần cuối: {latest_raw_cv.get('created_at', 'Vừa xong')}")
                if st.checkbox("Xem dữ liệu thô (Raw Text) đang lưu"):
                    st.code(latest_raw_cv['content'][:800] + "\n\n... [Đã cắt bớt]")
            with col_action:
                if st.button("🗑️ Xóa toàn bộ CV", type="secondary", use_container_width=True):
                    # Xóa toàn bộ liên quan đến CV của user này
                    for doc in cv_raw_docs + cv_analysis_docs:
                        db_client.delete_data("documents", {"id": doc['id']})
                    st.success("Đã xóa sạch dữ liệu CV khỏi hệ thống!")
                    time.sleep(1)
                    st.rerun()
        else:
            st.info("💡 Bạn chưa tải lên hồ sơ nào. Các thông tin tải lên sẽ được mã hóa an toàn và chỉ phục vụ cho việc AI Mentor tư vấn riêng cho bạn.")

    st.divider()

    # ==========================================
    # 2. DASHBOARD HIỂN THỊ KẾT QUẢ (Nếu đã có)
    # ==========================================
    if latest_analysis:
        try:
            analysis_data = json.loads(latest_analysis['content'])
            
            with st.container(border=True):
                st.markdown("### 📊 Tổng quan Hồ sơ")
                
                col_score, col_skills = st.columns([1, 2], gap="large")
                with col_score:
                    st.markdown("<p style='text-align: center; color: #666; font-weight: 600;'>ĐIỂM CHUẨN ATS</p>", unsafe_allow_html=True)
                    fig = create_donut_chart(analysis_data.get("score", 0), "Điểm")
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                with col_skills:
                    st.markdown("<p style='color: #666; font-weight: 600;'>🎯 KỸ NĂNG NỔI BẬT KHAI THÁC ĐƯỢC</p>", unsafe_allow_html=True)
                    # Vẽ Skill Chips bằng HTML
                    keywords = analysis_data.get("keywords", [])
                    html_chips = ""
                    for kw in keywords:
                        html_chips += f"<span style='display: inline-block; background-color: #E8F5E9; color: #2E7D32; padding: 6px 14px; border-radius: 20px; font-size: 14px; font-weight: 500; margin: 4px 6px 4px 0; border: 1px solid #C8E6C9;'>{kw}</span>"
                    st.markdown(html_chips, unsafe_allow_html=True)
                    
                    st.write("")
                    st.markdown(f"**💡 Lời khuyên từ AI Mentor:**<br>*{analysis_data.get('recommendation', '')}*", unsafe_allow_html=True)

                st.write("")
                col_pros, col_cons = st.columns(2, gap="medium")
                with col_pros:
                    with st.container(border=True):
                        st.markdown("<h5 style='color: #2E7D32;'>✅ Điểm sáng của CV</h5>", unsafe_allow_html=True)
                        for item in analysis_data.get("strengths", []):
                            st.markdown(f"- {item}")
                with col_cons:
                    with st.container(border=True):
                        st.markdown("<h5 style='color: #D32F2F;'>🚩 Vùng cần tối ưu</h5>", unsafe_allow_html=True)
                        for item in analysis_data.get("improvements", []):
                            st.markdown(f"- {item}")
            
            # Cung cấp nút để người dùng có thể tải CV mới đè lên
            st.write("")
            with st.expander("🔄 Tải lên bản CV cập nhật"):
                render_input_form(db_client, ai_client, user_id)

        except Exception as e:
            st.error(f"Lỗi hiển thị Dashboard: {e}")
            render_input_form(db_client, ai_client, user_id)
    else:
        # ==========================================
        # 3. KHU VỰC NHẬP LIỆU (Nếu chưa có dữ liệu)
        # ==========================================
        render_input_form(db_client, ai_client, user_id)


def render_input_form(db_client, ai_client, user_id):
    """Hàm phụ trợ để vẽ Form nhập liệu giúp code gọn gàng"""
    with st.container(border=True):
        tab_upload, tab_manual = st.tabs(["📤 Tải file CV (PDF)", "✍️ Điền tay (Dành cho người chưa có CV)"])
        
        cv_text_to_process = None
        source_type = None
        
        with tab_upload:
            uploaded_file = st.file_uploader("Kéo thả hoặc chọn file PDF", type=["pdf"])
            if st.button("🚀 Xử lý & Đánh giá CV", type="primary", key="btn_upload"):
                if uploaded_file:
                    cv_text_to_process = extract_text_from_pdf(uploaded_file)
                    source_type = "pdf_upload"
                else:
                    st.warning("Vui lòng tải file lên trước.")
                    
        with tab_manual:
            full_name = st.text_input("Họ và tên")
            education = st.text_area("Học vấn (Trường, chuyên ngành...)")
            experience = st.text_area("Kinh nghiệm làm việc / Hoạt động")
            skills = st.text_input("Kỹ năng chuyên môn (cách nhau bởi dấu phẩy)")
            if st.button("🚀 Lưu & Đánh giá hồ sơ", type="primary", key="btn_manual"):
                cv_text_to_process = f"HỒ SƠ CÁ NHÂN: {full_name}\nHỌC VẤN: {education}\nKINH NGHIỆM: {experience}\nKỸ NĂNG: {skills}"
                source_type = "manual_form"

        # Nếu có văn bản được submit, tiến hành quy trình xử lý kép (Embedding + JSON Analysis)
        if cv_text_to_process:
            process_and_save_cv(cv_text_to_process, source_type, user_id, db_client, ai_client)

def process_and_save_cv(text_content, source_type, user_id, db_client, ai_client):
    """Quy trình Xử lý Kép: Vừa nhúng Vector (cho AI Mentor) vừa lấy JSON (cho Dashboard)"""
    with st.spinner("🔄 Đang mã hóa hồ sơ và chạy thuật toán phân tích ATS..."):
        # 1. TẠO VECTOR ĐỂ LƯU TRỮ RAW TEXT (Đảm bảo logic cũ của cậu hoạt động)
        embedding = ai_client.generate_embedding(text_content)
        if embedding:
            db_client.insert_data("documents", {
                "content": text_content,
                "metadata": {"user_id": user_id, "source": source_type, "type": "personal_profile"},
                "embedding": embedding
            })

        # 2. GỌI AI ĐỂ PHÂN TÍCH VÀ XUẤT JSON (Cho Dashboard)
        system_prompt = """Bạn là chuyên gia phân tích CV. Hãy phân tích nội dung sau và trả về DUY NHẤT 1 chuỗi JSON hợp lệ. Không được có markdown (```json).
        Cấu trúc bắt buộc:
        {
            "score": (số nguyên 0-100 đánh giá CV),
            "keywords": [(5-7 từ khóa kỹ năng quan trọng tìm thấy)],
            "strengths": [(2-3 điểm mạnh rõ ràng)],
            "improvements": [(2-3 điểm cần cải thiện)],
            "recommendation": "(1 câu nhận xét tổng quan và khuyên hành động)"
        }"""
        
        try:
            # Gọi API (Lưu ý: Cậu có thể điều chỉnh payload sao cho hợp với OpenAIClient của cậu)
            payload = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Phân tích CV này:\n{text_content}"}
            ]
            ai_response = ai_client.generate_response(payload)
            
            # Làm sạch chuỗi trả về phòng trường hợp AI thêm markdown
            clean_json = ai_response.replace("```json", "").replace("```", "").strip()
            
            # Lưu bản phân tích JSON vào DB
            db_client.insert_data("documents", {
                "content": clean_json,
                "metadata": {"user_id": user_id, "source": "ai_analyzer", "type": "cv_analysis_result"}
            })
            
            st.success("🎉 Đã phân tích xong! Đang tải Dashboard...")
            time.sleep(1)
            st.rerun()
            
        except Exception as e:
            st.error(f"Lỗi trong quá trình phân tích AI: {e}")