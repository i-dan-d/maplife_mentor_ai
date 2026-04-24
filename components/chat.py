"""
Chat component module - Bản hoàn thiện Split-Column & Session State
"""
import streamlit as st
import uuid
from core.openai_client import OpenAIClient
from core.supabase_client import SupabaseClient

def chat_interface():
    # ==========================================
    # 1. KHỞI TẠO HỆ THỐNG VÀ XÁC THỰC
    # ==========================================
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

    # ==========================================
    # 2. TRUY XUẤT DỮ LIỆU CÁ NHÂN (CV & Tính cách)
    # ==========================================
    latest_cv = None
    latest_test = None
    has_any_data = False

    try:
        all_docs = db_client.query_data("documents", select_query="id, content, metadata") or []
        for doc in all_docs:
            meta = doc.get("metadata", {})
            if isinstance(meta, str):
                import json
                try: meta = json.loads(meta)
                except: pass
            
            db_user_id = str(meta.get("user_id", "")).strip()
            current_user_id = str(user_id).strip()
            
            if db_user_id == current_user_id:
                has_any_data = True
                source = meta.get("source", "")
                if source in ["pdf_upload", "manual_form"]:
                    latest_cv = doc.get('content')
                elif source == "personality_test":
                    latest_test = doc.get('content')
    except Exception as e:
        st.error(f"🔧 Lỗi truy xuất hồ sơ DB: {e}")

    # ==========================================
    # 3. TRUY XUẤT LỊCH SỬ CHAT VÀ QUẢN LÝ PHIÊN
    # ==========================================
    all_history = db_client.query_data("chat_history", filters={"user_id": user_id}) or []

    if "current_session_id" not in st.session_state:
        if all_history:
            latest_session = sorted(all_history, key=lambda x: x.get('created_at', ''), reverse=True)[0]
            st.session_state.current_session_id = latest_session.get('session_id')
        else:
            st.session_state.current_session_id = str(uuid.uuid4())

    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = []
        current_msgs = [msg for msg in all_history if msg.get('session_id') == st.session_state.current_session_id]
        current_msgs.sort(key=lambda x: x.get('created_at', ''))
        for m in current_msgs:
            if m.get('role') in ['user', 'assistant']:
                st.session_state.messages.append({"role": m['role'], "content": m['content']})

    # ==========================================
    # 4. VẼ GIAO DIỆN (SPLIT-COLUMN LAYOUT)
    # ==========================================
    col_hist, col_main = st.columns([1, 3], gap="medium")

    # --- CỘT TRÁI: LỊCH SỬ ---
    with col_hist:
        st.subheader("📜 Lịch sử")
        if st.button("➕ Đoạn chat mới", use_container_width=True, type="primary"):
            st.session_state.current_session_id = str(uuid.uuid4())
            if "messages" in st.session_state: del st.session_state.messages
            st.rerun()
        
        st.divider()
        sessions = {}
        for m in sorted(all_history, key=lambda x: x.get('created_at', '')):
            sid = m.get('session_id')
            if sid and sid not in sessions and m.get('role') == 'user':
                sessions[sid] = m.get('content', '')[:20] + "..."
        
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
        st.caption("🛠 Cài đặt")
        # Biến use_personal_data được khai báo ở đây để dùng cho cột bên phải
        use_personal_data = st.toggle("Dùng dữ liệu cá nhân", value=True)

    # --- CỘT PHẢI: KHUNG CHAT ---
    with col_main:
        st.header("💬 AI Mentor Chat")
        if has_any_data:
            st.caption("✅ Đã kết nối CV & Tính cách")
        else:
            st.caption("⚠️ Chưa có dữ liệu hồ sơ")

        # Hiển thị tin nhắn cũ
        chat_container = st.container(height=500)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Nhập liệu và Xử lý AI
        if prompt := st.chat_input("Hỏi MAPLIFE..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
            
            db_client.insert_data("chat_history", {
                "user_id": user_id,
                "session_id": st.session_state.current_session_id,
                "role": "user",
                "content": prompt
            })

            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Đang suy nghĩ..."):
                        if use_personal_data:
                            cv_val = latest_cv if latest_cv else "Chưa cung cấp CV."
                            test_val = latest_test if latest_test else "Chưa làm test."
                        else:
                            cv_val = "Bị chặn truy cập."
                            test_val = "Bị chặn truy cập."

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
                        
                        recent_history = st.session_state.messages[-2:] if len(st.session_state.messages) > 2 else st.session_state.messages
                        
                        payload_history = []
                        for idx, msg in enumerate(recent_history):
                            if idx == len(recent_history) - 1 and msg["role"] == "user":
                                hidden_command = f"{msg['content']}\n\n[System Note: Hãy trả lời với tư cách MAPLIFE do Nhóm 3 tạo ra]."
                                payload_history.append({"role": "user", "content": hidden_command})
                            else:
                                payload_history.append(msg)
                        
                        payload = [{"role": "system", "content": system_instruction}] + payload_history

                        response = ai_client.generate_response(payload)
                        st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            db_client.insert_data("chat_history", {
                "user_id": user_id,
                "session_id": st.session_state.current_session_id,
                "role": "assistant",
                "content": response
            })