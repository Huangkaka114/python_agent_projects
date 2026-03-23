# def scene_router(user_input: str) -> str:
#     """
#     根据用户输入自动判断场景
#     返回：life / office / query
#     """
#     user_input = user_input.lower()
#
#     if any(word in user_input for word in ["截图", "音乐", "打开", "播放", "系统"]):
#         return "life"
#     elif any(word in user_input for word in ["计算", "文件", "表格", "办公"]):
#         return "office"
#     else:
#         return "query"