import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from core.supabase_client import SupabaseClient

def render_sentiment_dashboard():
    user_id = st.session_state.get("user_id")
    if not user_id:
        return

    db_client = SupabaseClient()
    
    # Truy xuất dữ liệu
    logs = db_client.query_data("sentiment_log", filters={"user_id": user_id}) or []
    
    if not logs:
        st.info("Chưa có đủ dữ liệu tâm lý. Hãy trò chuyện thêm với AI Mentor để thu thập nhé!")
        return
        
    # Xử lý dữ liệu
    df = pd.DataFrame(logs)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values('created_at')
    
    # 7 ngày gần nhất
    seven_days_ago = datetime.now() - timedelta(days=7)
    # Lọc timezone an toàn
    try:
        df['created_at'] = df['created_at'].dt.tz_localize(None)
    except:
        pass
    
    recent_df = df[df['created_at'] >= pd.Timestamp(seven_days_ago)]
    
    st.markdown("### 💚 Sức khỏe tinh thần của bạn")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Gauge chart cho trạng thái hiện tại (dựa trên TB 3 tin nhắn cuối)
        if not recent_df.empty:
            current_score = recent_df.tail(3)['sentiment_score'].mean()
        else:
            current_score = df.tail(3)['sentiment_score'].mean()
            
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = current_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Trạng thái hiện tại", 'font': {'size': 16}},
            gauge = {
                'axis': {'range': [-1, 1], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "rgba(0,0,0,0)"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [-1, -0.3], 'color': '#FFCDD2'},  # Đỏ nhạt
                    {'range': [-0.3, 0.3], 'color': '#FFF9C4'}, # Vàng nhạt
                    {'range': [0.3, 1], 'color': '#C8E6C9'}     # Xanh nhạt
                ],
                'threshold': {
                    'line': {'color': "#2E7D32", 'width': 4},
                    'thickness': 0.75,
                    'value': current_score
                }
            }
        ))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Cảm xúc chủ đạo
        if not df.empty:
            top_emotions = df['dominant_emotion'].value_counts().head(3)
            st.markdown("**Cảm xúc thường gặp:**")
            for emotion, count in top_emotions.items():
                st.markdown(f"- {emotion} ({count} lần)")
    
    with col2:
        if len(df) > 1:
            # Line chart xu hướng
            fig_line = go.Figure()
            
            # Gộp theo ngày để có xu hướng rõ ràng
            df['date'] = df['created_at'].dt.date
            daily_df = df.groupby('date')['sentiment_score'].mean().reset_index()
            
            fig_line.add_trace(go.Scatter(
                x=daily_df['date'], 
                y=daily_df['sentiment_score'],
                mode='lines+markers',
                line=dict(color='#2E7D32', width=3),
                marker=dict(size=8, color='#1B5E20')
            ))
            
            fig_line.update_layout(
                title="Xu hướng cảm xúc",
                xaxis_title="Thời gian",
                yaxis_title="Điểm số (-1 đến 1)",
                yaxis=dict(range=[-1.1, 1.1]),
                height=250,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Cần thêm lịch sử trò chuyện để vẽ biểu đồ xu hướng.")
            
    # Hiển thị cảnh báo nếu có needs_support
    support_df = df[df['needs_support'] == True]
    if not support_df.empty:
        last_support = support_df.iloc[-1]
        time_diff = datetime.now() - last_support['created_at']
        if time_diff.days < 3: # Cảnh báo nếu trong 3 ngày qua có dấu hiệu
            st.warning(f"⚠️ Dường như gần đây bạn đang cảm thấy **{last_support['dominant_emotion']}**. Hãy nhớ nghỉ ngơi và đừng ngại chia sẻ nếu cần nhé!")
