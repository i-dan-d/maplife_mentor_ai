import json
from datetime import datetime, timedelta

def analyze_sentiment(text, openai_client):
    """
    Phân tích cảm xúc của người dùng dựa trên tin nhắn chat
    """
    prompt = f"""
    Phân tích cảm xúc của câu sau (bằng tiếng Việt):
    "{text}"
    Trả về ĐÚNG 1 ĐỊNH DẠNG JSON với cấu trúc sau:
    {{
      "label": "<positive|neutral|negative|anxious|motivated>",
      "score": <float -1.0 to 1.0>,
      "dominant_emotion": "<từ mô tả cảm xúc chính>",
      "keywords": ["từ khóa 1", "từ khóa 2"],
      "needs_support": <true|false>
    }}
    Chỉ trả về JSON, không thêm bất kỳ văn bản nào khác.
    """
    
    try:
        messages = [{"role": "user", "content": prompt}]
        # Gọi OpenAIClient với model hiện tại
        response_text = openai_client.generate_response(messages, temperature=0.3, max_tokens=200)
        
        # Làm sạch chuỗi trả về để trích xuất JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].strip()
            
        result = json.loads(response_text)
        
        # Đảm bảo có các field mặc định
        return {
            "sentiment_label": result.get("label", "neutral"),
            "sentiment_score": float(result.get("score", 0.0)),
            "dominant_emotion": result.get("dominant_emotion", "Bình thường"),
            "emotion_keywords": result.get("keywords", []),
            "needs_support": bool(result.get("needs_support", False)),
            "raw_analysis": result
        }
    except Exception as e:
        print(f"Lỗi khi phân tích cảm xúc: {e}")
        return {
            "sentiment_label": "neutral",
            "sentiment_score": 0.0,
            "dominant_emotion": "Không xác định",
            "emotion_keywords": [],
            "needs_support": False,
            "raw_analysis": {"error": str(e)}
        }
