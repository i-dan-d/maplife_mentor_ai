"""
OpenAI / Beeknoee client module (Sử dụng Python SDK)
"""
import openai
from config.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_EMBEDDING_MODEL, OPENAI_BASE_URL

class OpenAIClient:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY chưa được thiết lập.")
        
        self.api_key = OPENAI_API_KEY
        # Xóa dấu '/' ở cuối URL nếu có để tránh lỗi đường dẫn
        self.base_url = OPENAI_BASE_URL.rstrip('/') 
        self.model = OPENAI_MODEL
        self.embedding_model = OPENAI_EMBEDDING_MODEL

        # Khởi tạo OpenAI Client duy nhất dùng chung cho cả Chat và Embedding
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    # Cập nhật tham số đầu vào, thêm max_tokens=800
    def generate_response(self, messages, temperature=0.7, max_tokens=800):
        """
        Tạo phản hồi chat bằng Python SDK
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens  # --- THÊM DÒNG NÀY VÀO ĐÂY ---
            )
            # Trích xuất nội dung câu trả lời
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"[Error] SDK API (Chat Exception): {e}")
            return "Xin lỗi, hiện tại AI đang gặp sự cố. Bạn vui lòng thử lại nhé."

    def generate_embedding(self, text):
        """
        Tạo vector nhúng bằng Python SDK
        """
        try:
            text = text.replace("\n", " ") 
            response = self.client.embeddings.create(
                input=[text],
                model=self.embedding_model
            )
            # Trích xuất mảng vector
            return response.data[0].embedding
            
        except Exception as e:
            print(f"[Error] SDK API (Embedding Exception): {e}")
            return None