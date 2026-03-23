from AgentFlow.engine import check_permission
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from AgentFlow.utils import logger

# 定义状态
class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_role: str  # 加入角色，用于权限判断

# 流程图构建
def build_graph(llm, tools):

    # 1. 定义LLM节点
    def chat_node(state: State):
        response = llm.invoke(state["messages"])
        return {"messages": [response]}

    # 2. 定义路由（是否继续调用工具）
    def should_continue(state: State):
        last_msg = state["messages"][-1]
        if last_msg.tool_calls:
            # 获取第一个工具名
            tool_name = last_msg.tool_calls[0]["name"]
            user_role = state["user_role"]
            if not check_permission(tool_name, user_role):
                logger.warn(f"权限拒绝：角色[{user_role}] 无权调用工具[{tool_name}]")
                return END  # 无权 → 直接结束，不执行工具
            logger.info(f"权限通过：角色[{user_role}] 调用工具[{tool_name}]")
            return "tools"
        else:
            return END

    # 3. 构建图
    builder = StateGraph(State)

    # 4. 添加节点
    builder.add_node("chat", chat_node)
    builder.add_node("tools", ToolNode(tools))

    # 5. 构建边
    builder.add_edge(START, "chat")
    builder.add_conditional_edges(
        "chat",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    builder.add_edge("tools", "chat")

    # 6. 编译
    return builder.compile()