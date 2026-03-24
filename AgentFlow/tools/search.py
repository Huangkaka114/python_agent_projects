from AgentFlow.utils import permission
from langchain.tools import tool

@tool
@permission("user")
def web_search(query: str):
    """信息查询"""
    return "huangkaka 是一位专注于大模型应用开发的工程师"