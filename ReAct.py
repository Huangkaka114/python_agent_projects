import os
from dotenv import load_dotenv
# ✅ 最新版 LangChain 官方导入（不会再报错！）
from langchain_classic.agents import create_react_agent, AgentExecutor
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

# 运行
if __name__ == "__main__":
    question = "2026年人工智能最热门的方向是什么？"
    print("用户问题：", question)

    result = executor.invoke({"input": question})
    print("\n【最终回答】")
    print(result["output"])
