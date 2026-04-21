import streamlit as st
import PyPDF2
import uuid
from core.openai_client import OpenAIClient
from core.supabase_client import SupabaseClient

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted: text += extracted + "\n"
    return text

def save_cv_to_db(text_content, user_id, source_type):
    """Quy trình nhúng và lưu trữ chuẩn 1536-D"""
    ai_client = OpenAIClient()
    db_client = SupabaseClient()
    
    with st.spinner("Đang số hóa hồ sơ vào bộ nhớ AI..."):
        # 1. Tạo vector 1536 chiều
        embedding = ai_client.generate_embedding(text_content)
        
        if embedding:
            # 2. Lưu vào bảng documents
            db_client.insert_data("documents", {
                "content": text_content,
                "metadata": {
                    "user_id": user_id,
                    "source": source_type,
                    "type": "personal_profile"
                },
                "embedding": embedding
            })
            return True
    return False

def cv_analyzer():
    st.header("📄 Xây dựng Hồ sơ Cá nhân")
    
    db_client = SupabaseClient()
    user_id = st.session_state.get("user_id")

    # --- PHẦN MỚI: KIỂM TRA DỮ LIỆU HIỆN CÓ ---
    with st.expander("🔍 Kiểm tra trạng thái hồ sơ của bạn", expanded=True):
        existing_docs = db_client.query_data("documents", filters={"metadata->>user_id": user_id})
        
        if existing_docs:
            st.success(f"✅ Hệ thống đã ghi nhớ {len(existing_docs)} bản ghi hồ sơ của bạn.")
            # Hiển thị bản tin mới nhất
            latest_doc = existing_docs[-1]
            st.info(f"Cập nhật gần nhất: {latest_doc.get('created_at', 'Không rõ thời gian')}")
            if st.checkbox("Xem nội dung đang lưu trong bộ nhớ AI"):
                st.code(latest_doc['content'][:500] + "...")
        else:
            st.warning("⚠️ Bạn chưa có hồ sơ nào trong bộ nhớ. AI sẽ không thể tư vấn cá nhân hóa nếu thiếu thông tin này.")
    tab_upload, tab_manual = st.tabs(["📤 Tải CV có sẵn", "✍️ Điền thông tin (Template)"])

    # TAB 1: UPLOAD
    with tab_upload:
        uploaded_file = st.file_uploader("Tải file CV (PDF)", type=["pdf"])
        if uploaded_file and st.button("Xử lý file PDF"):
            text = extract_text_from_pdf(uploaded_file)
            if save_cv_to_db(text, user_id, "pdf_upload"):
                st.success("Đã lưu hồ sơ từ PDF thành công!")

    # TAB 2: MANUAL TEMPLATE
    with tab_manual:
        with st.form("cv_template_form"):
            st.subheader("Thông tin cơ bản")
            full_name = st.text_input("Họ và tên")
            education = st.text_area("Học vấn (Trường, chuyên ngành, niên khóa)")
            
            st.subheader("Năng lực & Kinh nghiệm")
            experience = st.text_area("Kinh nghiệm làm việc / Hoạt động ngoại khóa")
            projects = st.text_area("Các dự án đã tham gia (Ví dụ: MAPLIFE - Data for Impact 2026)")
            skills = st.text_input("Kỹ năng chuyên môn (cách nhau bởi dấu phẩy)")
            
            submit = st.form_submit_button("Lưu hồ sơ này")
            
            if submit:
                # Tạo văn bản cấu trúc để AI dễ đọc nhất
                structured_text = f"""
                HỒ SƠ CÁ NHÂN: {full_name}
                HỌC VẤN: {education}
                KINH NGHIỆM: {experience}
                DỰ ÁN TIÊU BIỂU: {projects}
                KỸ NĂNG: {skills}
                """
                if save_cv_to_db(structured_text, user_id, "manual_form"):
                    st.success("Đã tạo và lưu hồ sơ thành công!")