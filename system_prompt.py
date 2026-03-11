
from openai import OpenAI, api_key
from dotenv import load_dotenv
import os
load_dotenv()
# 加载环境变量（避免硬编码 API Key）
api_key = os.getenv('API_KEY')
base_url = os.getenv('BASE_URL')
client = OpenAI(
    api_key=api_key,
    base_url=base_url)

def basic_chat(prompt):
    """基础大模型调用函数"""
    try:
        # 发送请求
        response = client.chat.completions.create(
            model='deepseek-chat',
            messages=[
                # 必须有system 否则会出问题
                {"role": "system", "content": "You are a helpful assistant"},
                {"role":"user","content":prompt}
            ],
            # max_tokens=1024,
            temperature=0.5,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"调用失败：{e}"

# 程序入口判断语句
if __name__ == "__main__":
 result = basic_chat("你好，请告诉我你的年龄")
 print(result)
