import streamlit as st
from core.supabase_client import SupabaseClient
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
    # Xóa khoảng trắng thừa ở đầu/cuối và giữa các từ
    text = " ".join(text.split())
    # Giới hạn độ dài tối đa
    text = text[:max_length]
    return text

def community_board():
    st.markdown("<h2 style='text-align: center; color: #2E7D32;'>🌐 Cộng đồng MAPLIFE</h2>", unsafe_allow_html=True)
    
    user_id = st.session_state.get("user_id")
    auth_user = st.session_state.get("auth_user")
    
    if not user_id or not auth_user:
        st.warning("Vui lòng đăng nhập để tham gia cộng đồng.")
        return

    db = SupabaseClient()
    author_name = auth_user.email.split('@')[0]

    # ==========================================
    # 1. KHU VỰC ĐĂNG BÀI MỚI (CÓ LÀM SẠCH DỮ LIỆU)
    # ==========================================
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
                # LÀM SẠCH VÀ KIỂM TRA DỮ LIỆU TRƯỚC KHI LƯU
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

    # ==========================================
    # 2. KHU VỰC BẢNG TIN & TƯƠNG TÁC
    # ==========================================
    st.subheader("📰 Bảng tin mới nhất")
    
    # Kéo dữ liệu Bài viết và Bình luận cùng lúc
    all_posts = db.query_data("community_posts") or []
    all_comments = db.query_data("community_comments") or []
    
    if not all_posts:
        st.info("Cộng đồng đang yên ắng quá. Hãy là người mở bát đầu tiên đi cậu!")
        return

    sorted_posts = sorted(all_posts, key=lambda x: x.get('created_at', ''), reverse=True)

    for post in sorted_posts:
        post_id = post['id']
        # Lọc ra các bình luận thuộc về bài viết này
        post_comments = [c for c in all_comments if c.get('post_id') == post_id]
        
        with st.container(border=True):
            # Header bài viết
            c_avatar, c_meta, c_tag = st.columns([0.5, 8, 1.5], vertical_alignment="center")
            with c_avatar: st.markdown("### 👤")
            with c_meta:
                st.markdown(f"**{post.get('author_name', 'Ẩn danh')}**")
                st.caption(format_time(post.get('created_at', '')))
            with c_tag:
                cat = post.get('category', 'Chung')
                color = "#1976D2" if cat == "Hỏi đáp" else "#F57C00" if cat == "Kinh nghiệm" else "#2E7D32" if cat == "Khoe thành tích" else "#7B1FA2"
                st.markdown(f"<span style='background-color: {color}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px;'>{cat}</span>", unsafe_allow_html=True)

            # Nội dung chính
            st.markdown(f"#### {post.get('title', '')}")
            st.write(post.get('content', ''))
            
            # --- THANH TƯƠNG TÁC (LIKE & HIỂN THỊ SỐ BÌNH LUẬN) ---
            st.markdown("---")
            col_like, col_cmt_count, col_space = st.columns([2, 3, 5], vertical_alignment="center")
            with col_like:
                current_upvotes = post.get('upvotes', 0)
                if st.button(f"👍 Thích ({current_upvotes})", key=f"like_{post_id}", use_container_width=True):
                    db.update_data("community_posts", {"id": post_id}, {"upvotes": current_upvotes + 1})
                    st.rerun()
            with col_cmt_count:
                st.caption(f"💬 {len(post_comments)} Bình luận")

            # --- KHU VỰC BÌNH LUẬN ---
            with st.expander("Mở rộng bình luận"):
                # Hiển thị danh sách bình luận
                if post_comments:
                    for cmt in sorted(post_comments, key=lambda x: x.get('created_at', '')):
                        st.markdown(f"<div style='background-color: #f9f9f9; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #C8E6C9;'>"
                                    f"<b>{cmt.get('author_name', 'Ẩn danh')}</b> <span style='color: #888; font-size: 0.8em;'>({format_time(cmt.get('created_at', ''))})</span><br>"
                                    f"{cmt.get('content', '')}"
                                    f"</div>", unsafe_allow_html=True)
                else:
                    st.caption("Chưa có bình luận nào. Hãy là người đầu tiên!")
                
                # Form gửi bình luận mới
                with st.form(f"comment_form_{post_id}", clear_on_submit=True):
                    c_input, c_btn = st.columns([4, 1])
                    with c_input:
                        new_cmt = st.text_input("Nhập bình luận của bạn...", label_visibility="collapsed")
                    with c_btn:
                        submit_cmt = st.form_submit_button("Gửi")
                        
                    if submit_cmt:
                        safe_cmt = clean_text(new_cmt, 500) # Giới hạn CMT 500 ký tự
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