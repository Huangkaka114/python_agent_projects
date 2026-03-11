# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI, api_key
from dotenv import load_dotenv
# 加载 .env 文件中的环境变量（关键步骤）
# import os 是 Python 导入内置操作系统接口模块（os module） 的语句
load_dotenv()
api_key = os.environ.get('API_KEY')
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "你好，请告诉我今天日期？"},
    ],
    stream=False
)
# if __name__ == "__name__":
print(response.choices[0].message.content)