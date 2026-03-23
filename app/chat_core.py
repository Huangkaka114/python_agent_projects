from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from numpy.f2py.crackfortran import verbose

from sympy.physics.units import temperature


def create_agent(api_key: str, base_url: str, model: str):
    llm = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=0.1
    )
    # 联网搜索
    search = DuckDuckGoSearchRun()
    tools = [search]

    prompt = PromptTemplate.from_template("""
        # 任务
        你是一个严谨、可靠的智能助手，请严格按照规则回答用户问题。
        
        # 可用工具
        {tools}
        
        # 工具名称列表
        {tool_names}
        
        # 必须严格遵守的输出格式
        Question: {input}
        Thought: 分析是否需要使用工具，以及需要做什么
        Action: 仅在需要工具时填写，不需要则**整行省略**
        Action Input: 仅在有Action时填写，不需要则**整行省略**
        Observation: 仅在有工具返回时填写，不需要则**整行省略**
        Thought: 我已经可以给出最终答案
        Final Answer: 用中文清晰、完整地回答用户
        
        # 核心规则（违反则输出错误）
        1. 凡是**问候、闲聊、询问对话历史、询问上文、询问之前问题、询问记忆内容**，
           → **绝对不允许使用任何工具**，直接给出 Final Answer。
        2. 只有需要**实时信息、新闻、数据、外部知识**时，才允许使用搜索工具。
        3. 不需要工具时，**严禁出现 Action / Action Input / Observation** 任何一行。
        4. 回答必须使用中文，简洁、准确、不编造。
        5. 若问题可从对话历史直接得出，禁止调用工具。
        
        # 对话历史
        {history}
        
        # 开始
        Question: {input}
        Thought:{agent_scratchpad}""")

    # 五个占位符
    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True,max_iterations=3,early_stopping_method="generate")
    return executor
