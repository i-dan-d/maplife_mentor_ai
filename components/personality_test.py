import streamlit as st
import plotly.graph_objects as go
from core.supabase_client import SupabaseClient
import json

def interpret_big_five(o, c, e, a, n):
    report = []
    if o > 70: report.append("- **Tư duy:** Sáng tạo, thích đổi mới.")
    elif o < 40: report.append("- **Tư duy:** Thực tế, kỷ luật cao.")
    if c > 70: report.append("- **Kỷ luật:** Tận tâm, phù hợp làm quản lý.")
    if e > 70: report.append("- **Giao tiếp:** Hướng ngoại, năng lượng cao.")
    return "\n".join(report)

def create_radar_chart(categories, scores, title, color):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]], theta=categories + [categories[0]],
        fill='toself', fillcolor=f"rgba{tuple(list(int(color[1:][i:i+2], 16) for i in (0, 2, 4)) + [0.3])}",
        line=dict(color=color, width=2)
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=350, title=dict(text=title, x=0.5, font=dict(color=color)),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

def personality_test():
    st.header("🧪 Hồ sơ Tâm lý & Phong cách làm việc")
    user_id = st.session_state.get("user_id")
    db_client = SupabaseClient()

    # --- 1. LẤY DỮ LIỆU CŨ TỪ DB ĐỂ HIỂN THỊ NGAY ---
    if "test_data" not in st.session_state:
        existing = db_client.query_data("documents", filters={"metadata->>user_id": user_id, "metadata->>source": "personality_test"})
        if existing:
            # Giả sử cậu lưu dạng text, ta cần parse lại (tùy cách cậu lưu)
            st.session_state.test_data = existing[0]['content'] 
        else:
            st.session_state.test_data = None

    # --- 2. GIAO DIỆN CHÍNH ---
    with st.container(border=True):
        col_form, col_chart = st.columns([1, 1.2], gap="large")
        
        with col_form:
            st.subheader("📝 Cập nhật đánh giá")
            # Ở đây cậu để các sliders... (Tớ viết gọn để cậu dễ nhìn)
            h_r = st.slider("Realistic (R)", 0, 100, 50)
            h_i = st.slider("Investigative (I)", 0, 100, 50)
            h_a = st.slider("Artistic (A)", 0, 100, 50)
            h_s = st.slider("Social (S)", 0, 100, 50)
            h_e = st.slider("Enterprising (E)", 0, 100, 50)
            h_c = st.slider("Conventional (C)", 0, 100, 50)
            st.divider()
            bf_o = st.slider("Openness (O)", 0, 100, 50)
            bf_c = st.slider("Conscientiousness (C)", 0, 100, 50)
            bf_e = st.slider("Extraversion (E)", 0, 100, 50)
            bf_a = st.slider("Agreeableness (A)", 0, 100, 50)
            bf_n = st.slider("Neuroticism (N)", 0, 100, 50)
            
            if st.button("🚀 Lưu & Phân tích", type="primary", use_container_width=True):
                # Lưu vào DB và cập nhật Session State
                # (Logic insert/update như code cũ của cậu)
                st.session_state.test_data = "updated" # Đánh dấu để vẽ lại
                st.rerun()

        with col_chart:
            st.subheader("🕸️ Bản đồ năng lực")
            # Vẽ biểu đồ dựa trên giá trị slider hiện tại (Real-time)
            fig_h = create_radar_chart(['R','I','A','S','E','C'], [h_r, h_i, h_a, h_s, h_e, h_c], "RIASEC", "#2E7D32")
            st.plotly_chart(fig_h, use_container_width=True)
            
            fig_bf = create_radar_chart(['O','C','E','A','N'], [bf_o, bf_c, bf_e, bf_a, bf_n], "OCEAN", "#1976D2")
            st.plotly_chart(fig_bf, use_container_width=True)