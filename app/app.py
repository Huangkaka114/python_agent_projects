import os
import time

import streamlit as st
from chat_core import create_agent
from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory

st.set_page_config(page_title="Chat Agent", page_icon="🤖")
st.title("🤖 独立对话智能体")

# 环境配置
load_dotenv()
api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
model = "qwen-turbo"


if "chat_history" not in st.session_state:
    st.session_state.chat_history = InMemoryChatMessageHistory()

if "agent" not in st.session_state:
    executor = create_agent(api_key, base_url, model)


    agent_with_history = RunnableWithMessageHistory(executor, get_session_history=lambda
        session_id: st.session_state.chat_history,
                                                    input_messages_key="input", history_messages_key="history")
    st.session_state.agent = agent_with_history

# 消息历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 把所有聊天记录一条一条拿出来，每一条都放进对应的气泡里，然后把文字显示出来
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# 对话输入
user_input = st.chat_input("请输入问题...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            with st.spinner("🧠 AI 思考中..."):
                response = st.session_state.agent.invoke({"input": user_input},
                                                         config={"configurable": {"session_id": "huangkaka"}})
                full_response = response["output"]
            placeholder = st.empty()

            # 模拟流式（所有模型都稳定）
            temp = ""
            for char in full_response:
                temp += char
                placeholder.markdown(temp + "▌")
                time.sleep(0.01)

            placeholder.markdown(full_response)

        except Exception :
            full_response = "出现错误，请换个问题重试。"
            st.error(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})