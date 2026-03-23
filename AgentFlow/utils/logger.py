import logging
import os

# 确保日志目录存在
os.makedirs("storage/logs", exist_ok=True)

# 配置日志 → 强制 UTF-8
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 文件处理器（UTF-8）
file_handler = logging.FileHandler(
    "storage/logs/agent.log",
    encoding="utf-8"  # 关键修复
)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

logger.addHandler(file_handler)