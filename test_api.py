from openai import OpenAI
from config.config import OPENAI_API_KEY, OPENAI_BASE_URL
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL
)

response = client.chat.completions.create(
    model="claude-sonnet-4-6",
    messages=[
        {"role": "user", "content": "Xin chào!"}
    ]
)

print(response.choices[0].message.content)
