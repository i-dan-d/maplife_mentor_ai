import streamlit as st
import plotly.graph_objects as go
from core.supabase_client import SupabaseClient
import json

def personality_test():
    st.header("🧪 Trắc nghiệm Tính cách Nghề nghiệp (RIASEC)")
    st.caption("Hãy tự đánh giá mức độ phù hợp của bạn với các nhóm công việc dưới đây để MAPLIFE có thể tư vấn lộ trình chuẩn xác nhất!")

    # Bọc toàn bộ vào một Custom Card để đồng bộ UI
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    # Chia làm 2 cột: Cột Test và Cột Kết quả
    col_test, col_chart = st.columns([1, 1.2], gap="large")

    with col_test:
        st.subheader("📝 Tự đánh giá")
        st.write("Kéo thanh trượt theo mức độ bạn yêu thích/giỏi:")
        
        # 6 Nhóm tính cách Holland (RIASEC)
        r_score = st.slider("🛠 Kỹ thuật (Realistic)", 0, 100, 50, help="Thích làm việc với máy móc, công cụ, thực hành.")
        i_score = st.slider("🔬 Nghiên cứu (Investigative)", 0, 100, 50, help="Thích quan sát, tìm tòi, phân tích logic.")
        a_score = st.slider("🎨 Nghệ thuật (Artistic)", 0, 100, 50, help="Thích sáng tạo, thiết kế, tự do biểu đạt.")
        s_score = st.slider("🤝 Xã hội (Social)", 0, 100, 50, help="Thích giúp đỡ, giảng dạy, tư vấn cho người khác.")
        e_score = st.slider("💼 Quản lý (Enterprising)", 0, 100, 50, help="Thích lãnh đạo, kinh doanh, thuyết phục.")
        c_score = st.slider("📊 Nghiệp vụ (Conventional)", 0, 100, 50, help="Thích làm việc với số liệu, quy trình rõ ràng.")

        if st.button("💾 Lưu Hồ sơ Tính cách", type="primary", use_container_width=True):
            user_id = st.session_state.get("user_id")
            if user_id:
                # Lưu dữ liệu vào DB (Cậu có thể gọi Supabase ở đây)
                test_data = {
                    "Realistic": r_score, "Investigative": i_score,
                    "Artistic": a_score, "Social": s_score,
                    "Enterprising": e_score, "Conventional": c_score
                }
                # Ví dụ lưu: db_client.insert_data("documents", {"content": json.dumps(test_data), "metadata": {"user_id": user_id, "source": "personality_test"}})
                st.success("Đã cập nhật Hồ sơ Tính cách cho AI Mentor!")

    with col_chart:
        st.subheader("🕸️ Lưới Tính cách của bạn")
        
        # Dữ liệu trục và điểm số
        categories = ['Kỹ thuật', 'Nghiên cứu', 'Nghệ thuật', 'Xã hội', 'Quản lý', 'Nghiệp vụ']
        scores = [r_score, i_score, a_score, s_score, e_score, c_score]

        # VẼ BIỂU ĐỒ BẰNG PLOTLY
        fig = go.Figure()

        # Thêm trace cho Radar (Bắt buộc phải lặp lại phần tử đầu tiên để vẽ thành 1 vòng khép kín)
        fig.add_trace(go.Scatterpolar(
            r=scores + [scores[0]], 
            theta=categories + [categories[0]],
            fill='toself', 
            fillcolor='rgba(46, 125, 50, 0.4)', # Màu xanh lá cây MAPLIFE dạng trong suốt
            line=dict(color='#2E7D32', width=2), # Viền xanh lá đậm
            name='Điểm của bạn',
            marker=dict(size=8, color='#2E7D32')
        ))

        # Tùy chỉnh giao diện biểu đồ
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True, 
                    range=[0, 100], 
                    showticklabels=False, # Ẩn các con số trên trục cho đỡ rối
                    gridcolor="rgba(0,0,0,0.1)" # Màu lưới nhạt
                ),
                angularaxis=dict(
                    tickfont=dict(size=14, color="#1F2937") # Phông chữ cho các nhãn (Kỹ thuật, Xã hội...)
                ),
                bgcolor='rgba(0,0,0,0)' # LƯU Ý QUAN TRỌNG: Làm trong suốt nền của phần lưới
            ),
            paper_bgcolor='rgba(0,0,0,0)', # Làm trong suốt nền của toàn bộ khung biểu đồ
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            margin=dict(l=40, r=40, t=20, b=20),
            height=400
        )

        # Hiển thị biểu đồ lên Streamlit
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)