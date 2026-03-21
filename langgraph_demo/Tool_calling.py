import os
from typing import Annotated
from langchain.tools import tool
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph,END,START
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

# 让 AI 输出结构化指令 → 代码捕捉指令 → 执行真正功能 → 把结果丢回 AI
# START → chat（AI思考）
#            ↓（判断 tool_calls）
#     ┌──────┴──────┐
#     │             │
#   调用工具      直接回答
#     │             │
# 工具执行节点     END
#     │
# 回到 chat（循环）
load_dotenv()

@tool
def search(query: str):
    """用于搜索人物信息、最新知识、实时数据"""
    return "huangkaka 是一位热爱 AI 的极客，擅长 LangGraph、LLM 应用开发。"

@tool
def calculator(expression: str):
    """用于数学计算，输入纯数字表达式，如 1+1、2*3"""
    return f"计算结果：{eval(expression)}"

@tool
def weather(city: str):
    """查询城市天气，传入城市名，如 北京、上海"""
    return f"{city} 今天晴天，温度 25℃"

# 2.把工具列表传给 LLM
tools = [search,calculator,weather]

# 使用langChain的包装模型
llm = ChatOpenAI(
    base_url=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    model="qwen-turbo",
    temperature=0.1
).bind_tools(tools)  #绑定工具（结构化核心）

class State(TypedDict):
    messages:Annotated[list, add_messages]
    input: str


def chat_node(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: State):
    last_msg  = state["messages"][-1]
    # 如果 AI 输出了工具调用 → 走工具节点
    if last_msg.tool_calls:
        # 返回路由key
        return "tools" # 写死，永远不变
    else:
        return END

# 初始化图
builder = StateGraph(State)
# 节点
builder.add_node("chat",chat_node)

# 工具节点 自动执行工具
tool_node = ToolNode(tools)
builder.add_node("tools",tool_node)

# 边
builder.add_edge(START,"chat")
builder.add_conditional_edges(
    "chat",
    should_continue,
    {
        "tools": "tools", #当返回tools时，前往tools节点(上面的工具节点)
        END: END
    }
)

builder.add_edge("tools","chat")

graph = builder.compile()

if __name__ == "__main__":
    question = "介绍 huangkaka"
    # question = "123 × 456 等于多少"
    # question = "北京天气怎么样"

    initial_state = {
        "input": question,
        "messages": [
            ("system", "你必须遵守两条铁律：1. 你的知识库没有实时、外部数据 2. 不允许猜测、不允许编造、不允许解释词义。3. 只要不确定 → 立刻输出 tool_calls 调用search。"),
            ("user", question)
        ]
    }

    result = graph.invoke(initial_state)
    print("\n✅ 最终回答：\n", result["messages"][-1].content)