"""
Chat component module - Bản sửa lỗi Lịch sử và Tối ưu hóa Token
"""
import streamlit as st
import uuid
from core.openai_client import OpenAIClient
from core.supabase_client import SupabaseClient

def chat_interface():
    st.header("💬 AI Mentor Chat")
    
    # 1. Khởi tạo kết nối & Xác thực
    try:
        ai_client = OpenAIClient()
        db_client = SupabaseClient()
    except Exception as e:
        st.error(f"Lỗi khởi tạo hệ thống: {e}")
        return

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Lỗi xác thực người dùng. Vui lòng đăng nhập lại.")
        return
        
    st.caption(f"👤 User: **{user_id}**")

    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = str(uuid.uuid4())

    # ==========================================
    # 2. TỐI ƯU HÓA DỮ LIỆU: CHỈ LẤY BẢN MỚI NHẤT
    # ==========================================
    latest_cv = None
    latest_test = None
    has_any_data = False

    try:
        # 1. Kéo TẤT CẢ data (chỉ lấy id, content, metadata để không nghẽn mạng)
        # Bỏ qua bộ lọc SQL để tránh lỗi thư viện Supabase
        all_docs = db_client.query_data("documents", select_query="id, content, metadata") or []
        
        # 2. Lọc thủ công bằng Python (Tuyệt đối chính xác)
        for doc in all_docs:
            meta = doc.get("metadata", {})
            
            # Đề phòng Supabase trả về chuỗi JSON thay vì Dict
            if isinstance(meta, str):
                import json
                try: 
                    meta = json.loads(meta)
                except: 
                    pass
            
            # Ép kiểu về String để so sánh an toàn nhất
            db_user_id = str(meta.get("user_id", "")).strip()
            current_user_id = str(user_id).strip()
            
            if db_user_id == current_user_id:
                has_any_data = True
                source = meta.get("source", "")
                
                if source in ["pdf_upload", "manual_form"]:
                    latest_cv = doc.get('content')
                elif source == "personality_test":
                    latest_test = doc.get('content')
                    
        # 3. THÔNG BÁO DEBUG TRỰC QUAN
        if has_any_data:
            st.toast(f"✅ Đã kết nối thành công dữ liệu của user: {user_id}", icon="🎯")
        else:
            st.toast(f"⚠️ Cảnh báo: Không tìm thấy dữ liệu nào khớp với ID {user_id} trong DB!", icon="🕵️")

    except Exception as e:
        st.error(f"🔧 Lỗi truy xuất DB: {e}")

    # Lấy lịch sử chat
    all_history = db_client.query_data("chat_history", filters={"user_id": user_id}) or []

    # 2. CHIA GIAO DIỆN THÀNH 2 CỘT (Tỉ lệ 1:3)
    col_history, col_chat = st.columns([1, 3], gap="medium")

    # --- CỘT BÊN TRÁI: LỊCH SỬ VÀ CÀI ĐẶT ---
    with col_history:
        st.markdown("### 📜 Lịch sử")
        if st.button("➕ Đoạn chat mới", use_container_width=True, type="primary"):
            st.session_state.current_session_id = str(uuid.uuid4())
            if "messages" in st.session_state: del st.session_state.messages
            st.rerun()
        
        st.divider()
        
        # Hiển thị danh sách các phiên chat cũ
        sessions = {}
        for msg in sorted(all_history, key=lambda x: x.get('created_at', '')):
            sid = msg.get('session_id')
            if sid and sid not in sessions and msg.get('role') == 'user':
                sessions[sid] = msg.get('content', '')[:20] + "..."
        
        if not sessions:
            st.caption("Chưa có lịch sử.")
        else:
            for sid, title in sessions.items():
                is_current = (sid == st.session_state.current_session_id)
                if st.button(f"{'📍' if is_current else '💬'} {title}", key=f"nav_{sid}", use_container_width=True):
                    st.session_state.current_session_id = sid
                    if "messages" in st.session_state: del st.session_state.messages
                    st.rerun()
        
        st.divider()
        use_personal_data = st.toggle("Sử dụng dữ liệu cá nhân", value=True)

    # --- CỘT BÊN PHẢI: KHUNG TRÒ CHUYỆN CHÍNH ---
    with col_chat:
        st.header("💬 AI Mentor Chat")
        
        if has_any_data:
            st.caption("✅ Đã kết nối CV & Tính cách")
        
        # 🟢 THÊM 2 DÒNG BẢO HIỂM NÀY VÀO ĐÂY:
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        chat_container = st.container(height=500)
        with chat_container:
            # Lỗi ở dòng dưới này sẽ biến mất vì messages đã được tạo ở trên!
            for message in st.session_state.messages: 
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    # --- XỬ LÝ TIN NHẮN MỚI ---
    if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        db_client.insert_data("chat_history", {
            "user_id": user_id,
            "session_id": st.session_state.current_session_id,
            "role": "user",
            "content": prompt
        })

        with st.chat_message("assistant"):
            with st.spinner("Đang kết nối trí nhớ AI..."):
                # --- 1. KIỂM TRA QUYỀN TRUY CẬP (CHECKBOX) ---
                if use_personal_data:
                    # Tận dụng luôn các biến latest_cv, latest_test đã query từ đầu trang!
                    cv_val = latest_cv if latest_cv else "Người dùng chưa cung cấp CV."
                    test_val = latest_test if latest_test else "Người dùng chưa làm bài test tính cách."
                    
                    if has_any_data:
                        st.toast("🧠 AI đang sử dụng trí nhớ cá nhân của bạn.", icon="✅")
                else:
                    cv_val = "Người dùng KHÔNG cho phép truy cập CV trong phiên này."
                    test_val = "Người dùng KHÔNG cho phép truy cập tính cách trong phiên này."

                # --- 2. XÂY DỰNG SYSTEM PROMPT "BỌC THÉP" VÀO THẺ XML ---
        
                system_instruction = f"""[LỆNH QUẢN TRỊ DANH TÍNH TỐI CAO]
                1. Tên của bạn là MAPLIFE - Một người bạn đồng hành trên hành trình sự nghiệp cuộc sống.
                2. Bạn được phát triển bởi Nhóm 3 [DFI]Maplife cho cuộc thi Data for Impact 2026.
                3. TUYỆT ĐỐI KHÔNG nhận mình là Claude, ChatGPT, AI assistant hay sản phẩm của Anthropic/OpenAI. Nếu ai hỏi "Bạn là ai?" hay "Ai tạo ra bạn?", hãy tự hào giới thiệu bạn là MAPLIFE của Nhóm 3 và sau khi giới thiệu cậu là ai thì hãy cho họ xem cậu có thể làm gì.

                [DỮ LIỆU BẮT BUỘC VỀ NGƯỜI DÙNG]
                <USER_PROFILE>
                <CV_CONTENT>{cv_val}</CV_CONTENT>
                <PERSONALITY>{test_val}</PERSONALITY>
                </USER_PROFILE>

                HƯỚNG DẪN TƯ VẤN:
                1. Sử dụng dữ liệu trong thẻ XML trên để tư vấn cá nhân hóa. 
                2. Tuyệt đối không phủ nhận việc có dữ liệu nếu các thẻ trên đã chứa nội dung.
                3. Xưng "tôi" và gọi người dùng là "bạn" (hoặc xưng hô thân thiện). Trả lời bằng tiếng Việt súc tích, chuyên nghiệp.
                NHIỆM VỤ: 
                1. Nếu trong thẻ <USER_PROFILE> có dữ liệu thực, BẮT BUỘC phải dùng nó để cá nhân hóa câu trả lời. Tuyệt đối không được nói 'Tôi không có thông tin'.
                2. Nếu dữ liệu báo là KHÔNG cho phép truy cập, hãy nhắc người dùng tích vào ô 'Sử dụng dữ liệu' ở thanh Sidebar bên trái.
                3. Nếu dữ liệu báo là chưa cung cấp, hãy hướng dẫn họ sang tab 'Xây dựng Hồ sơ CV' hoặc 'Trắc nghiệm tính cách' để bổ sung.
                HƯỚNG DẪN:
                1. Đóng vai trò là một Coach (Huấn luyện viên) khai vấn. 
                2. Hạn chế đưa ra lời khuyên trực tiếp ngay lập tức. Thay vào đó, hãy đặt 1-2 câu hỏi phản biện để người dùng tự suy ngẫm về kỹ năng và mục tiêu của họ.
                3. Chỉ đưa ra lộ trình cụ thể khi người dùng thực sự bế tắc hoặc yêu cầu rõ ràng.
                4. Cậu tên là Maplife.
                """

                # --- 3. GIỚI HẠN LỊCH SỬ CHAT (Chỉ lấy 2 tin nhắn gần nhất) ---
                recent_history = st.session_state.messages[-2:] if len(st.session_state.messages) > 2 else st.session_state.messages
                
                # 3. VŨ KHÍ TỐI THƯỢNG: Kẹp lệnh ẩn vào tin nhắn cuối cùng của User
                payload_history = []
                for idx, msg in enumerate(recent_history):
                    # Nếu là tin nhắn cuối cùng (câu hỏi hiện tại của người dùng)
                    if idx == len(recent_history) - 1 and msg["role"] == "user":
                        hidden_command = f"{msg['content']}\n\n[System Note: Hãy trả lời với tư cách là MAPLIFE AI do Nhóm 3 - Học viện Ngân hàng tạo ra. Tuyệt đối KHÔNG nhắc đến chữ Claude, Anthropic hay OpenAI]."
                        payload_history.append({"role": "user", "content": hidden_command})
                    else:
                        payload_history.append(msg)
                
                # 4. Gộp thành payload hoàn chỉnh
                payload = [{"role": "system", "content": system_instruction}] + payload_history

                # 5. Gọi AI
                response = ai_client.generate_response(payload)
                st.markdown(response)
        
        # Lưu vào UI và DB cho câu trả lời của AI
        st.session_state.messages.append({"role": "assistant", "content": response})
        db_client.insert_data("chat_history", {
            "user_id": user_id,
            "session_id": st.session_state.current_session_id,
            "role": "assistant",
            "content": response
        })