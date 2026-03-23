import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在目录
ENV_PATH = os.path.join(BASE_DIR, "../config/.env")    # 绝对定位
load_dotenv(dotenv_path=ENV_PATH)
def get_llm(tools,config):
    llm = ChatOpenAI(
        base_url=os.getenv("BASE_URL"),
        api_key=os.getenv("API_KEY"),
        model=os.getenv("MODEL_NAME"),
        temperature=config["model"]["temperature"],
        max_tokens=config["model"]["max_tokens"]
    )
    return llm.bind_tools(tools, tool_choice="auto")


