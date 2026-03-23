def permission(role: str):
    """
        工具权限注解
        使用：@permission("admin") / @permission("user") / @permission("guest")
    """
    def decorator(func):
        func.permission = role # 把权限绑定到函数上
        return func
    return decorator