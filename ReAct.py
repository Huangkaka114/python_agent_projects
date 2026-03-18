import os
from dotenv import load_dotenv
from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# pip install -U ddgs
# 加载环境
load_dotenv()

# LLM
llm = ChatOpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
    model="qwen-turbo",
    temperature=0.1
)

store = {}

# get_session_history 是一个工厂函数,它接收 session_id,返回对应这个用户的 BaseChatMessageHistory 对象
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


# 搜索工具
search = DuckDuckGoSearchRun()
tools = [search]

# ReAct 官方提示词
prompt = PromptTemplate.from_template("""
Answer the following questions as best you can.

You have access to the following tools:
{tools}

Use the following format:
Question: the input question
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
Thought: I now know the final answer
Final Answer: the final answer to the original input question

This is the conversation history:
{history}

Begin!
Question: {input}
Thought:{agent_scratchpad}
""")

# 创建 Agent
agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

message_history = RunnableWithMessageHistory(executor, get_session_history=get_session_history,
                                             input_messages_key="input", history_messages_key="history")

# 运行
if __name__ == "__main__":
    while True:
        question = input("\n请输入问题：")
        if question.lower() in ["exit", "quit", "q"]:
            print("结束对话")
            break
        # session_id用来区分不同用户,传递给get_session_history
        result = message_history.invoke({"input": question},config={"configurable": {"session_id": "huangkaka"}})
        print("\n【最终回答】")
        print(result["output"])
