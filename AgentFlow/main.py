from core import build_graph, get_llm, load_memory, save_memory
from engine import check_permission, PermissionDeniedError, LLMCallError, ToolNotFoundError
from langchain_core.messages import SystemMessage,HumanMessage
from tools import get_tools
from utils import logger, save_graph_png, load_yaml, get_user_role
from prompts import load_system_prompt
from langgraph.graph import MessagesState
import os

def main():
    # 1. 初始化配置、日志（工程化必备）
    logger.info("=== AgentFlow 智能体启动 ===")
    # 加载配置文件（config/settings.yaml）
    config = load_yaml("config/settings.yaml")
    # 加载系统提示词（prompts/system.txt）
    system_prompt = load_system_prompt()
    # 2. 初始化工具列表、大模型、流程图谱
    tools = get_tools()
    # 绑定工具与大模型（强制工具调用逻辑）
    llm = get_llm(tools,config)
    # 构建LangGraph流程图谱
    graph = build_graph(llm, tools)
    # 生成流程可视化图（保存至storage目录，面试可展示）
    # save_graph_png(graph)

    # 4. 读取用户输入与身份
    user_input = "帮我发一封邮件给 3294141452@qq.com，标题：测试AI邮件，正文：你的Agent已经支持自动发邮件了,附件在storage/assets/test.png"
    user_role = "admin"


    # 3. 加载指定角色持久化记忆
    state = load_memory(user_role)
    # print(state)
    logger.info(f"加载历史记忆：用户角色={get_user_role(state)}，历史对话数={len(state['messages'])}")

    # 拼接系统提示词 + 用户输入，确保Agent严格遵循规则 state更新
    if not state["messages"]:
        state["messages"].append(SystemMessage(content=system_prompt))

    # 追加用户输入（累加，不清空）
    state["messages"].append(HumanMessage(content=user_input))

    try:
        # 6. 执行流程图谱，调用工具（核心逻辑）
        result = graph.invoke(state)

        # 8. 输出结果，保存最新记忆（持久化）
        print("\n✅ AgentFlow 响应：", result["messages"][-1].content)
        print(result)
        save_memory(result, user_role)
        logger.info("运行完成，已保存最新记忆")

    except Exception as e:
        print(f"\n❌ 系统异常：{str(e)}")
        logger.error(f"系统未知异常：{str(e)}")
    finally:
        logger.info("=== AgentFlow 智能体运行结束 ===\n")

if __name__ == "__main__":
    # 确保storage目录存在（避免日志、记忆文件保存失败）
    if not os.path.exists("storage"):
        os.makedirs("storage")
    if not os.path.exists("storage/logs"):
        os.makedirs("storage/logs")
    # 启动项目
    main()