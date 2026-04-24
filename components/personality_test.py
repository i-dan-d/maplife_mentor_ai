import streamlit as st
import plotly.graph_objects as go
import json
from core.supabase_client import SupabaseClient
import time

def create_radar_chart(categories, scores, title, color):
    """Hàm vẽ biểu đồ Radar đồng bộ với phong cách Glassmorphism"""
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]], theta=categories + [categories[0]],
        fill='toself', fillcolor=f"rgba{tuple(list(int(color[1:][i:i+2], 16) for i in (0, 2, 4)) + [0.3])}",
        line=dict(color=color, width=3),
        marker=dict(size=8)
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, gridcolor="rgba(0,0,0,0.1)")),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=350, title=dict(text=title, x=0.5, font=dict(size=16, color=color)),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

def personality_test():
    st.markdown("<h2 style='text-align: center; color: #2E7D32;'>🧪 Hồ sơ Năng lực & Tính cách</h2>", unsafe_allow_html=True)
    
    db_client = SupabaseClient()
    user_id = st.session_state.get("user_id")
    
    if not user_id:
        st.warning("Vui lòng đăng nhập để xem hồ sơ.")
        return

    # ==========================================
    # 1. TRUY XUẤT DỮ LIỆU ĐÃ LƯU (DATABASE FIRST)
    # ==========================================
    with st.spinner("Đang nạp hồ sơ từ Cloud..."):
        existing_docs = db_client.query_data("documents", filters={"metadata->>user_id": user_id, "metadata->>source": "personality_test"})
    
    saved_data = None
    if existing_docs:
        try:
            # Parse chuỗi JSON từ cột content
            saved_data = json.loads(existing_docs[0]['content'])
        except:
            saved_data = None

    # ==========================================
    # 2. HIỂN THỊ HỒ SƠ HIỆN TẠI (DÀNH CHO VISION BOARD)
    # ==========================================
    if saved_data:
        with st.container(border=True):
            st.subheader("🌟 Chân dung năng lực của bạn")
            st.info(f"💡 Dữ liệu này sẽ được dùng để cá nhân hóa **Vision Board** và **AI Mentor**.")
            
            c1, c2 = st.columns(2)
            with c1:
                h_data = saved_data['holland']
                fig_h = create_radar_chart(list(h_data.keys()), list(h_data.values()), "Định hướng (RIASEC)", "#2E7D32")
                st.plotly_chart(fig_h, use_container_width=True)
            with c2:
                bf_data = saved_data['big_five']
                fig_bf = create_radar_chart(list(bf_data.keys()), list(bf_data.values()), "Phong cách (OCEAN)", "#1976D2")
                st.plotly_chart(fig_bf, use_container_width=True)
            
            with st.expander("🔍 Xem chi tiết dữ liệu máy (JSON Formats)"):
                st.json(saved_data)
    else:
        st.info("👋 Bạn chưa có hồ sơ năng lực. Hãy thực hiện bài tự đánh giá bên dưới nhé!")

    st.divider()

    # ==========================================
    # 3. FORM CẬP NHẬT (INTERFACE)
    # ==========================================
    st.subheader("📝 Cập nhật/Tạo mới hồ sơ")
    with st.container(border=True):
        tab_h, tab_bf = st.tabs(["🎯 Mô hình Holland", "🧠 Mô hình Big Five"])
        
        with tab_h:
            col1, col2 = st.columns(2)
            with col1:
                h_r = st.slider("Realistic (R)", 0, 100, saved_data['holland']['R'] if saved_data else 50)
                h_i = st.slider("Investigative (I)", 0, 100, saved_data['holland']['I'] if saved_data else 50)
                h_a = st.slider("Artistic (A)", 0, 100, saved_data['holland']['A'] if saved_data else 50)
            with col2:
                h_s = st.slider("Social (S)", 0, 100, saved_data['holland']['S'] if saved_data else 50)
                h_e = st.slider("Enterprising (E)", 0, 100, saved_data['holland']['E'] if saved_data else 50)
                h_c = st.slider("Conventional (C)", 0, 100, saved_data['holland']['C'] if saved_data else 50)

        with tab_bf:
            col3, col4 = st.columns(2)
            with col3:
                bf_o = st.slider("Openness (O)", 0, 100, saved_data['big_five']['O'] if saved_data else 50)
                bf_c = st.slider("Conscientiousness (C)", 0, 100, saved_data['big_five']['C'] if saved_data else 50)
                bf_e = st.slider("Extraversion (E)", 0, 100, saved_data['big_five']['E'] if saved_data else 50)
            with col4:
                bf_a = st.slider("Agreeableness (A)", 0, 100, saved_data['big_five']['A'] if saved_data else 50)
                bf_n = st.slider("Neuroticism (N)", 0, 100, saved_data['big_five']['N'] if saved_data else 50)

        if st.button("🚀 LƯU HỒ SƠ CLOUD", type="primary", use_container_width=True):
            # Tính mã Holland nhanh
            h_scores = {'Realistic': h_r, 'Investigative': h_i, 'Artistic': h_a, 'Social': h_s, 'Enterprising': h_e, 'Conventional': h_c}
            top_code = sorted(h_scores.items(), key=lambda x: x[1], reverse=True)[0][0]

            # Đóng gói JSON
            new_payload = {
                "holland": {"R": h_r, "I": h_i, "A": h_a, "S": h_s, "E": h_e, "C": h_c},
                "big_five": {"O": bf_o, "C": bf_c, "E": bf_e, "A": bf_a, "N": bf_n},
                "meta": {"primary_trait": top_code, "last_updated": str(st.session_state.get('user_id'))}
            }
            
            json_str = json.dumps(new_payload, ensure_ascii=False)
            
            if saved_data:
                db_client.update_data("documents", {"id": existing_docs[0]['id']}, {"content": json_str})
            else:
                db_client.insert_data("documents", {"content": json_str, "metadata": {"user_id": user_id, "source": "personality_test"}})
            
            st.success("Hồ sơ đã được đồng bộ hóa!")
            time.sleep(1)
            st.rerun()