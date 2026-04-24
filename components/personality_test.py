import streamlit as st
import plotly.graph_objects as go
import json
import time
from core.supabase_client import SupabaseClient

def get_preliminary_assessment(h_scores, bf_scores):
    """Hàm đưa ra nhận định nhanh dựa trên điểm số hiện tại"""
    # Lấy 2 nhóm Holland cao nhất
    top_h = sorted(h_scores.items(), key=lambda x: x[1], reverse=True)[:2]
    h_code = f"{top_h[0][0]}{top_h[1][0]}"
    
    assessment = f"### 💡 Nhận định sơ bộ: **Nhóm {h_code}**\n"
    
    # Logic nhận định nhanh Holland
    if "A" in h_code and "I" in h_code:
        assessment += "- Bạn là người có tư duy phân tích nhưng không thiếu sự sáng tạo. Phù hợp với các ngành như AI, Thiết kế hệ thống, hoặc Nghiên cứu trải nghiệm.\n"
    elif "E" in h_code and "S" in h_code:
        assessment += "- Bạn có thiên hướng lãnh đạo và hỗ trợ cộng đồng. Rất tiềm năng trong mảng Quản trị nhân sự hoặc Điều hành dự án xã hội.\n"
    else:
        assessment += "- Dựa trên điểm số, bạn có xu hướng làm việc tốt nhất trong các môi trường đề cao tính thực tế và chuyên môn hóa.\n"

    # Logic nhận định nhanh Big Five
    if bf_scores['C'] > 70:
        assessment += "- **Điểm cộng:** Sự kỷ luật cao của bạn là chìa khóa để hoàn thành các lộ trình dài hạn mà MAPLIFE đề xuất."
    
    return assessment

def create_radar_chart(categories, scores, title, color):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]], theta=categories + [categories[0]],
        fill='toself', fillcolor=f"rgba{tuple(list(int(color[1:][i:i+2], 16) for i in (0, 2, 4)) + [0.3])}",
        line=dict(color=color, width=3)
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, gridcolor="rgba(0,0,0,0.1)")),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=320, title=dict(text=title, x=0.5, font=dict(size=16, color=color)),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

def personality_test():
    st.markdown("<h2 style='text-align: center; color: #2E7D32;'>🧪 Phân tích Năng lực & Tính cách</h2>", unsafe_allow_html=True)
    
    db_client = SupabaseClient()
    user_id = st.session_state.get("user_id")

    # 1. LOAD DỮ LIỆU CŨ (Nếu có)
    existing_docs = db_client.query_data("documents", filters={"metadata->>user_id": user_id, "metadata->>source": "personality_test"})
    saved_data = json.loads(existing_docs[0]['content']) if existing_docs else None

    # 2. GIAO DIỆN CHÍNH (Real-time)
    with st.container(border=True):
        col_input, col_display = st.columns([1, 1.2], gap="large")

        with col_input:
            st.subheader("📝 Điều chỉnh chỉ số")
            tab_h, tab_bf = st.tabs(["🎯 Holland (RIASEC)", "🧠 Big Five (OCEAN)"])
            
            with tab_h:
                h_r = st.slider("Realistic (Kỹ thuật)", 0, 100, saved_data['holland']['R'] if saved_data else 50)
                h_i = st.slider("Investigative (Nghiên cứu)", 0, 100, saved_data['holland']['I'] if saved_data else 50)
                h_a = st.slider("Artistic (Nghệ thuật)", 0, 100, saved_data['holland']['A'] if saved_data else 50)
                h_s = st.slider("Social (Xã hội)", 0, 100, saved_data['holland']['S'] if saved_data else 50)
                h_e = st.slider("Enterprising (Quản lý)", 0, 100, saved_data['holland']['E'] if saved_data else 50)
                h_c = st.slider("Conventional (Nghiệp vụ)", 0, 100, saved_data['holland']['C'] if saved_data else 50)

            with tab_bf:
                bf_o = st.slider("Openness (Trải nghiệm)", 0, 100, saved_data['big_five']['O'] if saved_data else 50)
                bf_c = st.slider("Conscientiousness (Kỷ luật)", 0, 100, saved_data['big_five']['C'] if saved_data else 50)
                bf_e = st.slider("Extraversion (Hướng ngoại)", 0, 100, saved_data['big_five']['E'] if saved_data else 50)
                bf_a = st.slider("Agreeableness (Hòa đồng)", 0, 100, saved_data['big_five']['A'] if saved_data else 50)
                bf_n = st.slider("Neuroticism (Áp lực)", 0, 100, saved_data['big_five']['N'] if saved_data else 50)

            # Nút Lưu dữ liệu
            if st.button("🚀 LƯU HỒ SƠ LÊN CLOUD", type="primary", use_container_width=True):
                payload = {
                    "holland": {"R": h_r, "I": h_i, "A": h_a, "S": h_s, "E": h_e, "C": h_c},
                    "big_five": {"O": bf_o, "C": bf_c, "E": bf_e, "A": bf_a, "N": bf_n}
                }
                json_str = json.dumps(payload, ensure_ascii=False)
                if saved_data:
                    db_client.update_data("documents", {"id": existing_docs[0]['id']}, {"content": json_str})
                else:
                    db_client.insert_data("documents", {"content": json_str, "metadata": {"user_id": user_id, "source": "personality_test"}})
                st.toast("Đã đồng bộ hóa hồ sơ!", icon="✅")

        with col_display:
            st.subheader("📊 Bản đồ Năng lực")
            # BIỂU ĐỒ HIỂN THỊ NGAY LẬP TỨC
            fig_h = create_radar_chart(['R','I','A','S','E','C'], [h_r, h_i, h_a, h_s, h_e, h_c], "RIASEC Profile", "#2E7D32")
            st.plotly_chart(fig_h, use_container_width=True)
            
            # ĐÁNH GIÁ SƠ BỘ (Cập nhật Real-time)
            st.markdown("---")
            assessment_text = get_preliminary_assessment(
                {'R':h_r,'I':h_i,'A':h_a,'S':h_s,'E':h_e,'C':h_c},
                {'O':bf_o,'C':bf_c,'E':bf_e,'A':bf_a,'N':bf_n}
            )
            st.markdown(assessment_text)

    # Hiển thị lịch sử cũ dưới dạng JSON để debug/kiểm tra nếu cần
    if saved_data:
        with st.expander("📂 Xem dữ liệu JSON đang lưu trên Cloud"):
            st.json(saved_data)