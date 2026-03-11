
from openai import OpenAI
from dotenv import load_dotenv
import os
from pyexpat.errors import messages

load_dotenv()
api_key = os.getenv('API_KEY')
base_url = os.getenv('BASE_URL')
client = OpenAI(
    api_key=api_key,
    base_url=base_url)

def few_shot_chat(user_input):
# 少样本提示：给示例让模型按格式回答
    messages = [
        {"role":"system","content":"你是代码解释助手，按「功能+思路+代码」格式回答"},
        # 样本示例1
        {"role":"user","content":"解释 print('hello')"},
        {"role":"assistant","content":"功能：输出字符串'hello'到控制台\n思路：调用print函数，传入字符串参数\n代码：print('hello')"},
        # 样本示例2
        {"role": "user", "content": "解释 a = [1,2,3]"},
        {"role": "assistant","content": "功能：创建一个包含1、2、3的列表并赋值给变量a\n思路：用列表语法[]定义列表，赋值给变量a\n代码：a = [1,2,3]"},
        # 用户提问
        {"role":"user","content":user_input}
    ]
    try:
         response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.5
        )
         return response.choices[0].message.content
    except Exception as e:
        print(e)

if __name__ == '__main__':
    print(few_shot_chat("解释 for i in range(5): print(i)"))