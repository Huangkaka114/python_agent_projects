from typing import Annotated
from dotenv import load_dotenv
from langgraph.graph import StateGraph,START,END
from openai import OpenAI
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
import os
load_dotenv()
# chat 客户端初始化
api_key = os.getenv('API_KEY')
base_url = os.getenv('BASE_URL')
client = OpenAI(
    api_key=api_key,
    base_url=base_url)

#定义了一个字典结构，名字叫 State，它必须包含：
# messages → 列表类型
# input → 字符串类型
# 少一个、类型错一个 → 直接报错。
# messages:Annotated[list,add_messages] LangGraph 自动把消息包装成对象
# HumanMessage / AIMessage  数据示例
# HumanMessage(
#     content="介绍LangGraph",
#     id="some-id-123",
#     type="human"      # 关键标识
# )
class State(TypedDict):
    messages:Annotated[list,add_messages] #自动合并历史
    input:str

# 初始化StateGraph
builder = StateGraph(State)
# 定义聊天节点函数
def chat_node(state: State):
    formatted_messages = []
    print(state)
    # 遍历 LangGraph 自动封装的消息对象
    for msg in state["messages"]:
        # 读取对象的 type 和 content（官方标准）
        if msg.type == "system":
            formatted_messages.append({"role": "system", "content": msg.content})
        elif msg.type == "human":
            formatted_messages.append({"role": "user", "content": msg.content})
        else:
            formatted_messages.append({"role": "assistant", "content": msg.content})
    # print("消息对象打印",formatted_messages)
    "调用llm"
    # messages = state["messages"]
    response = client.chat.completions.create(model="qwen-turbo",messages=formatted_messages,temperature=0.1)

    # 获取回答
    content = response.choices[0].message.content
    # print("chat回答:", content)
    # 返回给 LangGraph（自动合并历史）
    return {"messages": [{"role":"assistant", "content": content}]}

# 条件判断函数
def should_continue(state: State):
    last_message = state["messages"][-1].content
    # print(f"last_message:{last_message}")
    if "需要调用工具" in last_message:
        return 'search_tool'
    else: return END

def search_tool(state: State):
    # print("需要调用工具")
    # 返回新消息
    return {"messages": [{"role": "assistant", "content": "已成功通过工具获取数据"}]}

# 添加节点
builder.add_node("chat_node", chat_node)
builder.add_node("should_continue", should_continue)
builder.add_node("search_tool", search_tool)

# 连接边 START → chat → END
builder.add_edge(START,"chat_node")
# builder.add_edge("chat",END)

# 条件边
builder.add_conditional_edges(
    "chat_node", # 1. 从哪个节点出发
    should_continue, # 2. 判断函数（决定走哪条路）
    {
        "search_tool": "search_tool", # 3. 路由映射表
        END: END
    }
)
builder.add_edge("search_tool", "chat_node")

# 编译图
graph = builder.compile()


if __name__ == "__main__":
    initial_state = {
        "input": "介绍LangGraph",
        "messages": [{"role":"system","content":"""你是一个带工具的循环助手。

    规则：
    1 需要最新数据、外网、计算 → 先说：需要调用工具
    2 拿到工具结果 → 整理、合成回答
    3 不需要工具 → 直接正常回答
    不要瞎编，不知道就去查。"""},{"role": "user", "content": "介绍huangkaka"}]
    }

    # 运行图
    result = graph.invoke(initial_state)
    # AI回答： {'messages': [HumanMessage(content='介绍LangGraph', additional_kwargs={}, response_metadata={}, id='77def323-f5b3-48ce-b482-fae869b2284a'), AIMessage(content='LangGraph 是一个用于构建和运行 **基于图的流程**（graph-based workflows）的框架，特别适用于 **大型语言模型（LLM）应用** 的复杂工作流管理。它允许开发者将多个任务、工具、模型或 API 组合成一个有向无环图（DAG），从而实现更高效、可扩展和可维护的 AI 应用。\n\n---\n\n## 🌟 什么是 LangGraph？\n\nLangGraph 是由 [LangChain](https://www.langchain.com/) 团队开发的一个库，旨在帮助开发者构建 **复杂的 AI 工作流**，特别是在处理多步骤、条件分支、循环、并行任务等场景时非常有用。\n\n它的核心思想是：**将整个应用流程建模为一个图结构**，每个节点代表一个任务或操作，边表示任务之间的依赖关系。\n\n---\n\n## 🧠 核心概念\n\n### 1. **节点（Node）**\n- 每个节点代表一个任务或操作。\n- 可以是 LLM 调用、工具调用、数据处理、条件判断等。\n\n### 2. **边（Edge）**\n- 表示节点之间的依赖关系或控制流。\n- 可以是静态的（固定顺序）或动态的（根据输出决定下一步）。\n\n### 3. **图（Graph）**\n- 所有节点和边组成的结构。\n- 支持 **有向无环图（DAG）** 或 **有向循环图（DAG with loops）**。\n\n### 4. **状态（State）**\n- 图中所有节点共享的状态对象。\n- 用于在不同节点之间传递数据。\n\n---\n\n## 🚀 主要功能\n\n### ✅ 复杂流程管理\n- 支持条件分支（if/else）\n- 支持循环（for/while）\n- 支持并行执行多个任务\n\n### ✅ 易于扩展\n- 可以集成任何 LLM、工具、API\n- 支持自定义节点和逻辑\n\n### ✅ 可调试性\n- 提供详细的日志和调试信息\n- 支持可视化流程（如通过 Graphviz）\n\n### ✅ 高性能\n- 支持异步执行\n- 可优化任务调度\n\n---\n\n## 🧩 示例代码（简单流程）\n\n```python\nfrom langgraph import Graph, State\n\n# 定义状态类\nclass MyState(State):\n    text: str = ""\n\n# 定义节点函数\ndef node_a(state: MyState):\n    state.text += "A"\n    return state\n\ndef node_b(state: MyState):\n    state.text += "B"\n    return state\n\n# 创建图\ngraph = Graph()\n\n# 添加节点\ngraph.add_node("a", node_a)\ngraph.add_node("b", node_b)\n\n# 添加边\ngraph.add_edge("a", "b")\n\n# 设置入口节点\ngraph.set_entry_point("a")\n\n# 运行流程\nresult = graph.run(MyState())\nprint(result.text)  # 输出: AB\n```\n\n---\n\n## 🧩 适用场景\n\n- **客服聊天机器人**：根据用户输入选择不同的处理路径\n- **数据分析流水线**：多个数据处理步骤，可能有分支和条件\n- **自动化任务系统**：如生成报告、邮件发送、数据清洗等\n- **多模型协作**：多个 LLM 模型协同完成复杂任务\n\n---\n\n## 📦 安装\n\n```bash\npip install langgraph\n```\n\n---\n\n## 📘 文档与资源\n\n- 官方文档：[https://langgraph.dev/](https://langgraph.dev/)\n- GitHub 仓库：[https://github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)\n- 社区和教程：[https://discord.gg/6qVwXpYJ7j](https://discord.gg/6qVwXpYJ7j)\n\n---\n\n## 🔁 与 LangChain 的关系\n\nLangGraph 是 LangChain 生态的一部分，主要用于构建 **复杂的工作流**，而 LangChain 更侧重于 **LLM 的调用和链式处理**。两者结合可以构建出强大的 AI 应用。\n\n---\n\n如果你有具体的使用场景或问题，我可以帮你设计一个 LangGraph 流程！需要我帮你写一个实际的例子吗？', additional_kwargs={}, response_metadata={}, id='7caa6e07-0792-4acd-b6b3-0629e18dd4b4', tool_calls=[], invalid_tool_calls=[])], 'input': '介绍LangGraph'}
    print("AI回答：", result["messages"][-1].content)