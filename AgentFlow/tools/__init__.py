from pathlib import Path
# 存放最终收集到的所有工具
_auto_tools = []

here = Path(__file__).parent
# glob 就是用来在文件夹里「按规则找文件」的工具
for f in here.glob('*.py'):
    # 文件名去掉后缀
    name = f.stem
    # 跳过自己和基类
    if name in ("__init__", "base"):
        continue
    # 动态导入模块
    mod = __import__(f"tools.{name}", fromlist=["*"])
    # vars(mod).values() 把模块里所有东西，变成一个字典 取出字典里的所有值
    for obj in vars(mod).values():
        # hasattr = has attribute → 有没有这个属性？ 两个属性同时存在 → 100% 是 LangChain @tool 工具
        if hasattr(obj, "name") and hasattr(obj, "func"):
            _auto_tools.append(obj)

def get_tools():
    """自动返回所有 @tool 工具列表，不用手动维护"""
    return _auto_tools

# 规定别人导入时：只会导出 get_tools 工程化规范，避免污染命名空间
__all__ = ["get_tools"]