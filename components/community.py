import streamlit as st
import json
from core.supabase_client import SupabaseClient
from core.clustering_engine import run_clustering
import time
import re

def format_time(timestamp_str):
    """Hàm làm gọn thời gian hiển thị"""
    try:
        return timestamp_str.split('T')[0] + " " + timestamp_str.split('T')[1][:5]
    except:
        return timestamp_str

def clean_text(text, max_length):
    """Hàm làm sạch dữ liệu: Cắt khoảng trắng, giới hạn độ dài, xóa ký tự lạ"""
    if not text: return ""
    text = " ".join(text.split())
    text = text[:max_length]
    return text

def render_feed(db, user_id, author_name):
    """Render Tab 1: Bảng tin"""
    with st.expander("✍️ Chia sẻ câu chuyện, kinh nghiệm hoặc đặt câu hỏi..."):
        with st.form("new_post_form", clear_on_submit=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                post_title = st.text_input("Tiêu đề bài viết", placeholder="Tối đa 100 ký tự...")
            with col2:
                post_category = st.selectbox("Chủ đề", ["Hỏi đáp", "Khoe thành tích", "Kinh nghiệm", "Review"])
            
            post_content = st.text_area("Nội dung chi tiết", height=150, placeholder="Viết gì đó hữu ích nhé (Tối đa 2000 ký tự)...")
            submit_post = st.form_submit_button("🚀 Đăng bài", type="primary")

            if submit_post:
                safe_title = clean_text(post_title, 100)
                safe_content = clean_text(post_content, 2000)

                if len(safe_title) < 5 or len(safe_content) < 10:
                    st.warning("⚠️ Tiêu đề (ít nhất 5 ký tự) và Nội dung (ít nhất 10 ký tự) không được để trống hoặc quá ngắn!")
                else:
                    with st.spinner("Đang xử lý..."):
                        db.insert_data("community_posts", {
                            "user_id": user_id,
                            "author_name": author_name,
                            "title": safe_title,
                            "content": safe_content,
                            "category": post_category
                        })
                        st.success("Bài viết đã được lên sóng!")
                        time.sleep(1)
                        st.rerun()

    st.divider()
    st.subheader("📰 Bảng tin mới nhất")
    
    all_posts = db.query_data("community_posts") or []
    all_comments = db.query_data("community_comments") or []
    
    if not all_posts:
        st.info("Cộng đồng đang yên ắng quá. Hãy là người mở bát đầu tiên đi cậu!")
        return

    sorted_posts = sorted(all_posts, key=lambda x: x.get('created_at', ''), reverse=True)

    for post in sorted_posts:
        post_id = post['id']
        post_comments = [c for c in all_comments if c.get('post_id') == post_id]
        
        with st.container(border=True):
            c_avatar, c_meta, c_tag = st.columns([0.5, 8, 1.5], vertical_alignment="center")
            with c_avatar: st.markdown("### 👤")
            with c_meta:
                st.markdown(f"**{post.get('author_name', 'Ẩn danh')}**")
                st.caption(format_time(post.get('created_at', '')))
            with c_tag:
                cat = post.get('category', 'Chung')
                color = "#1976D2" if cat == "Hỏi đáp" else "#F57C00" if cat == "Kinh nghiệm" else "#2E7D32" if cat == "Khoe thành tích" else "#7B1FA2"
                st.markdown(f"<span style='background-color: {color}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px;'>{cat}</span>", unsafe_allow_html=True)

            st.markdown(f"#### {post.get('title', '')}")
            st.write(post.get('content', ''))
            
            st.markdown("---")
            col_like, col_cmt_count, col_space = st.columns([2, 3, 5], vertical_alignment="center")
            with col_like:
                current_upvotes = post.get('upvotes', 0)
                if st.button(f"👍 Thích ({current_upvotes})", key=f"like_{post_id}", use_container_width=True):
                    db.update_data("community_posts", {"id": post_id}, {"upvotes": current_upvotes + 1})
                    st.rerun()
            with col_cmt_count:
                st.caption(f"💬 {len(post_comments)} Bình luận")

            with st.expander("Mở rộng bình luận"):
                if post_comments:
                    for cmt in sorted(post_comments, key=lambda x: x.get('created_at', '')):
                        st.markdown(f"<div style='background-color: #f9f9f9; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #C8E6C9;'>"
                                    f"<b>{cmt.get('author_name', 'Ẩn danh')}</b> <span style='color: #888; font-size: 0.8em;'>({format_time(cmt.get('created_at', ''))})</span><br>"
                                    f"{cmt.get('content', '')}"
                                    f"</div>", unsafe_allow_html=True)
                else:
                    st.caption("Chưa có bình luận nào. Hãy là người đầu tiên!")
                
                with st.form(f"comment_form_{post_id}", clear_on_submit=True):
                    c_input, c_btn = st.columns([4, 1])
                    with c_input:
                        new_cmt = st.text_input("Nhập bình luận của bạn...", label_visibility="collapsed")
                    with c_btn:
                        submit_cmt = st.form_submit_button("Gửi")
                        
                    if submit_cmt:
                        safe_cmt = clean_text(new_cmt, 500)
                        if len(safe_cmt) > 0:
                            db.insert_data("community_comments", {
                                "post_id": post_id,
                                "user_id": user_id,
                                "author_name": author_name,
                                "content": safe_cmt
                            })
                            st.rerun()
                        else:
                            st.warning("Bình luận không được để trống!")

def render_matching(db, user_id, author_name):
    """Render Tab 2: Kết nối"""
    st.subheader("🤝 Kết nối những người cùng chí hướng")
    st.caption("MAPLIFE sử dụng thuật toán Clustering để tìm kiếm và phân nhóm bạn với những người có chung định hướng và đặc điểm tính cách.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("💡 **Gợi ý:** Cập nhật mục tiêu nghề nghiệp của bạn trong Hồ sơ để MAPLIFE kết nối chính xác hơn nhé!")
    with col2:
        if st.button("🔄 Tìm nhóm ngay", use_container_width=True, type="primary"):
            with st.spinner("Đang chạy thuật toán kết nối đa chiều..."):
                all_docs = db.query_data("documents", filters={"metadata->>source": "personality_test"}) or []
                
                users_data = []
                user_profiles = {}
                
                for doc in all_docs:
                    uid = doc.get("metadata", {}).get("user_id")
                    if uid:
                        try:
                            profile = json.loads(doc.get("content", "{}"))
                            user_profiles[uid] = profile
                        except:
                            pass
                            
                for uid, profile in user_profiles.items():
                    users_data.append({"user_id": uid, "profile": profile})
                
                if len(users_data) >= 2:
                    updates = run_clustering(users_data)
                    for update in updates:
                        db.delete_data("user_clusters", {"user_id": update["user_id"]})
                        db.insert_data("user_clusters", update)
                    st.success("Đã tìm thấy những người bạn mới!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.warning("Cần ít nhất 2 người dùng đã làm bài test tính cách để hệ thống có thể ghép nhóm.")
                    
    # Lấy thông tin nhóm của user hiện tại
    my_cluster = db.query_data("user_clusters", filters={"user_id": user_id})
    if my_cluster:
        my_cluster = my_cluster[0]
        cluster_id = my_cluster.get('cluster_id')
        cluster_label = my_cluster.get('cluster_label')
        
        st.markdown(f"### 🌟 Bạn thuộc: **{cluster_label}**")
        
        # Lấy tất cả user cùng nhóm
        peers = db.query_data("user_clusters", filters={"cluster_id": cluster_id}) or []
        peers = [p for p in peers if p.get('user_id') != user_id]
        
        if not peers:
            st.write("Hiện tại bạn là người tiên phong trong nhóm này. Hãy chờ thêm những người bạn khác nhé!")
            return
            
        st.markdown(f"**Có {len(peers)} người bạn cùng nhóm với bạn:**")
        
        user_info_list = db.query_data("users") or []
        user_info_dict = {u['id']: u for u in user_info_list}
        
        for peer in sorted(peers, key=lambda x: x.get('similarity_score', 0)):
            peer_id = peer.get('user_id')
            peer_info = user_info_dict.get(peer_id, {})
            
            # Chỉ hiển thị public users
            if not peer_info.get('is_public', True):
                continue
                
            p_name = peer_info.get('display_name') or peer_info.get('name') or "Người dùng ẩn danh"
            p_goal = peer_info.get('career_goal') or "Đang khám phá bản thân"
            
            with st.container(border=True):
                col_ava, col_info, col_act = st.columns([1, 7, 2], vertical_alignment="center")
                with col_ava:
                    st.markdown("## 🧑‍💻")
                with col_info:
                    st.markdown(f"**{p_name}**")
                    st.caption(f"🎯 Mục tiêu: {p_goal}")
                with col_act:
                    if st.button("👋 Chào hỏi", key=f"hello_{peer_id}", use_container_width=True):
                        st.toast(f"Đã gửi lời chào đến {p_name}!", icon="👋")
    else:
        st.info("Bạn chưa được xếp nhóm. Nhấn 'Tìm nhóm ngay' để bắt đầu kết nối nhé!")

def community_board():
    st.markdown("<h2 style='text-align: center; color: #2E7D32;'>🌐 Cộng đồng MAPLIFE</h2>", unsafe_allow_html=True)
    
    user_id = st.session_state.get("user_id")
    auth_user = st.session_state.get("auth_user")
    
    if not user_id or not auth_user:
        st.warning("Vui lòng đăng nhập để tham gia cộng đồng.")
        return

    db = SupabaseClient()
    author_name = auth_user.email.split('@')[0]
    
    tab_feed, tab_matching = st.tabs(["📰 Bảng tin", "🤝 Kết nối"])
    
    with tab_feed:
        render_feed(db, user_id, author_name)
        
    with tab_matching:
        render_matching(db, user_id, author_name)