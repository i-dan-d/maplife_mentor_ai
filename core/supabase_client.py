"""
Supabase client module
"""

from supabase import create_client, Client
from config.config import get_secret

class SupabaseClient:
    def search_documents(self, query_embedding, user_id, threshold=0.1, limit=3):
        """Truy xuất các đoạn CV liên quan từ Database"""
        try:
            response = self.client.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': threshold, # Ngưỡng 0.1 để dễ dàng lấy ra CV
                    'match_count': limit,
                    'p_user_id': user_id
                }
            ).execute()
            return response.data
        except Exception as e:
            print(f"Lỗi tìm kiếm RAG: {str(e)}")
            return []
    def __init__(self):
        # CHỈ LẤY CHÌA KHÓA LÚC NÀY (Vì lúc này st.secrets ĐÃ SẴN SÀNG)
        url = get_secret("SUPABASE_URL")
        key = get_secret("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError(f"Chưa có Key! URL: {bool(url)}, KEY: {bool(key)}")
            
        # Khởi tạo kết nối đến Supabase
        self.client: Client = create_client(url, key)

    def insert_data(self, table_name, data):
        """
        Chèn dữ liệu vào bảng. 
        :param data: có thể là dict (1 dòng) hoặc list of dicts (nhiều dòng).
        """
        try:
            response = self.client.table(table_name).insert(data).execute()
            return response.data
        except Exception as e:
            print(f"[Error] Supabase Insert ({table_name}): {e}")
            return None

    def delete_data(self, table_name, filters):
        """Xóa dữ liệu dựa trên bộ lọc (filters)"""
        try:
            query = self.client.table(table_name).delete()
            for key, value in filters.items():
                # Bổ sung dòng này để hỗ trợ xóa dữ liệu JSONB
                if "->>" in key:
                    query = query.filter(key, "eq", value)
                else:
                    query = query.eq(key, value)
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"[Error] Supabase Delete ({table_name}): {e}")
            return None

    def query_data(self, table_name, select_query="*", filters=None):
        try:
            query = self.client.table(table_name).select(select_query)
            if filters:
                for key, value in filters.items():
                    # Hỗ trợ lọc JSONB (metadata->>user_id)
                    if "->>" in key:
                        query = query.filter(key, "eq", value)
                    else:
                        query = query.eq(key, value)
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"[Error] Supabase Query ({table_name}): {e}")
            return None
            
    def update_data(self, table_name, match_conditions, update_data):
        """
        Cập nhật dữ liệu có sẵn.
        :param match_conditions: Cột dùng để tìm record, vd: {"id": 1}
        :param update_data: Dữ liệu mới cần update.
        """
        try:
            query = self.client.table(table_name).update(update_data)
            for key, value in match_conditions.items():
                query = query.eq(key, value)
                
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"[Error] Supabase Update ({table_name}): {e}")
            return None