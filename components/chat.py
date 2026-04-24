"""
Chat component module - Tích hợp Knowledge Router Đa Nguồn (RAG)
"""
import streamlit as st
import uuid
from core.openai_client import OpenAIClient
from core.supabase_client import SupabaseClient
import time

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
        use_personal_data = st.toggle("Dùng dữ liệu cá nhân", value=True)

        with st.expander("🗑 Vùng nguy hiểm"):
            if st.button("Xóa đoạn chat này", use_container_width=True):
                db_client.delete_data("chat_history", {"user_id": user_id, "session_id": st.session_state.current_session_id})
                if "messages" in st.session_state: del st.session_state.messages
                st.toast("Đã xóa lịch sử!", icon="🗑️")
                st.rerun()

    # --- CỘT PHẢI: KHUNG CHAT ---
    with col_main:
        st.header("💬 AI Mentor Chat")
        if has_any_data:
            st.caption("✅ Đã kết nối CV & Tính cách")
        else:
            st.caption("⚠️ Chưa có dữ liệu hồ sơ")

        chat_container = st.container(height=500)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

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
                    with st.spinner("MAPLIFE đang tra cứu dữ liệu ngành..."):
                        
                        # ==========================================
                        # 🌟 KIẾN TRÚC MỚI: BỘ ĐIỀU HƯỚNG TRI THỨC LÊN NGÔI (ROUTER)
                        # ==========================================
                        prompt_lower = prompt.lower()
                        matched_tables = set() # Dùng set để tránh trùng lặp bảng

                        # Từ điển định tuyến: Dễ dàng thêm từ khóa hoặc thêm bảng mới sau này
                        routing_rules = {
                            "book": ["sách", "đọc", "tài liệu", "giáo trình", "book"],
                            "courses": ["khóa học", "chứng chỉ", "đào tạo", "học", "course"],
                            "reddit_amas": ["kinh nghiệm", "thực tế", "phỏng vấn", "khuyên", "review", "làm sao"],
                            "occupations": ["ngành", "nghề", "lương", "công việc", "tương lai", "lộ trình", "jd"]
                        }

                        # Quét câu hỏi xem dính từ khóa của bảng nào
                        for table, keywords in routing_rules.items():
                            if any(kw in prompt_lower for kw in keywords):
                                matched_tables.add(table)

                        # Nếu câu hỏi quá chung chung không trúng từ nào, chọc vào 2 bảng bao quát nhất
                        if not matched_tables:
                            matched_tables = {"occupations", "reddit_amas"}

                        internet_context = ""
                        try:
                            # 1. Mã hóa câu hỏi thành Vector
                            prompt_embedding = ai_client.generate_embedding(prompt)
                            
                            # 2. Truy xuất dữ liệu từ các bảng đã được định tuyến
                            for table in matched_tables:
                                res = db_client.client.rpc('match_knowledge', {
                                    'query_embedding': prompt_embedding,
                                    'match_threshold': 0.72, # Độ chính xác trên 72% mới lấy
                                    'match_count': 2,        # Lấy 2 kết quả tốt nhất của mỗi bảng
                                    'table_name': table
                                }).execute()
                                
                                if res.data:
                                    internet_context += f"\n--- TRÍCH XUẤT TỪ: {table.upper()} ---\n"
                                    internet_context += "\n".join([d['content'] for d in res.data])
                        except Exception as e:
                            print(f"Lỗi hệ thống RAG: {e}")

                        # ==========================================
                        # LẮP RÁP PROMPT CHO AI
                        # ==========================================
                        if use_personal_data:
                            cv_val = latest_cv if latest_cv else "Chưa cung cấp CV."
                            test_val = latest_test if latest_test else "Chưa làm bài test tính cách."
                        else:
                            cv_val = "Bị chặn truy cập."
                            test_val = "Bị chặn truy cập."

                        system_instruction = f"""[LỆNH QUẢN TRỊ DANH TÍNH TỐI CAO]
                        1. Tên của bạn là MAPLIFE - Một người bạn đồng hành trên hành trình sự nghiệp.
                        2. Bạn được phát triển bởi Nhóm 3 [DFI]Maplife.
                        3. TUYỆT ĐỐI KHÔNG nhận mình là Claude, ChatGPT hay sản phẩm của Anthropic/OpenAI.

                        [1. DỮ LIỆU CÁ NHÂN CỦA USER]
                        <CV_CONTENT>{cv_val}</CV_CONTENT>
                        <PERSONALITY>{test_val}</PERSONALITY>

                        [2. DỮ LIỆU KIẾN THỨC CHUYÊN NGÀNH (BẮT BUỘC THAM KHẢO NẾU CÓ)]
                        Dưới đây là các tài liệu thực tế trích xuất từ database để trả lời câu hỏi:
                        <KNOWLEDGE_BASE>
                        {internet_context if internet_context else "Không có dữ liệu ngoại vi nào khớp với câu hỏi này."}
                        </KNOWLEDGE_BASE>

                        Hãy đóng vai Coach khai vấn, xưng "tôi" gọi "bạn". 
                        Nếu bạn sử dụng thông tin từ KNOWLEDGE_BASE, hãy khéo léo lồng ghép nó vào lời khuyên.
                        """
                        
                        recent_history = st.session_state.messages[-3:] if len(st.session_state.messages) > 3 else st.session_state.messages
                        
                        payload_history = []
                        for idx, msg in enumerate(recent_history):
                            if idx == len(recent_history) - 1 and msg["role"] == "user":
                                hidden_command = f"{msg['content']}\n\n[System Note: Nhớ tuân thủ vai trò MAPLIFE do Nhóm 3 tạo ra]."
                                payload_history.append({"role": "user", "content": hidden_command})
                            else:
                                payload_history.append(msg)
                        
                        payload = [{"role": "system", "content": system_instruction}] + payload_history

                        # Gọi OpenAI
                        response = ai_client.generate_response(payload)

                    # Hiệu ứng gõ chữ
                    def stream_generator(text):
                        import time
                        for word in text.split(" "):
                            yield word + " "
                            time.sleep(0.01)
                    
                    st.write_stream(stream_generator(response))
            
            # Lưu Data
            st.session_state.messages.append({"role": "assistant", "content": response})
            db_client.insert_data("chat_history", {
                "user_id": user_id,
                "session_id": st.session_state.current_session_id,
                "role": "assistant",
                "content": response
            })