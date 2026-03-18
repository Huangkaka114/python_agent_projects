import sys
sys.stdin.reconfigure(encoding='utf-8')
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import chromadb
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

# ===================== 加载环境变量 & 初始化客户端 =====================
load_dotenv()

# 初始化阿里云百炼客户端（兼容 OpenAI 接口）
client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL")
)

# 核心配置
EMBEDDING_MODEL = "text-embedding-v4"  # 阿里云百炼嵌入模型
LLM_MODEL = "qwen-turbo"  # 阿里云百炼大模型（通义千问，中文友好）
VECTOR_DB_PATH = "./aliyun_rag_chroma"  # 向量库存储路径
DOCUMENT_PATH = "doc/news_content.txt"  # 本地文档路径


# ===================== 核心工具函数 =====================
def get_embedding_by_aliyun(text: str) -> List[float]:
    """
    调用阿里云百炼 text-embedding-v4 生成嵌入向量
    :param text: 输入文本
    :return: 嵌入向量（text-embedding-v4 默认输出 768 维）
    """
    if not text.strip():
        print("⚠️ 输入文本为空，无法生成嵌入")
        return []

    try:
        # 调用阿里云百炼嵌入接口
        completion = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text.strip()
        )
        # 解析嵌入向量
        embedding = completion.data[0].embedding
        print(f"✅ 文本「{text[:20]}...」嵌入生成成功，维度：{len(embedding)}")
        return embedding
    except Exception as e:
        print(f"❌ 生成嵌入向量失败：{e}")
        return []


def load_and_split_document(file_path: str) -> List[str]:
    """
    加载本地文档并切分（适配中文文本）
    :param file_path: 文档路径
    :return: 切分后的文本块列表
    """
    # 自动创建测试文档（如果不存在）
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if not os.path.exists(file_path):
        test_content = """
        通义千问（Qwen）是阿里云研发的大语言模型，支持多轮对话、文本生成、知识问答等场景。
        阿里云百炼（Model Studio）是一站式大模型开发平台，提供嵌入模型、大语言模型等多种能力。
        text-embedding-v4 是阿里云百炼推出的轻量级文本嵌入模型，输出768维向量，适合RAG场景。
        RAG（检索增强生成）的核心是先检索相关文档，再基于文档生成回答，能有效解决大模型幻觉问题。
        使用阿里云百炼构建RAG的步骤：1.文档切分 2.生成嵌入向量 3.存入向量库 4.检索 5.生成回答。
        """
        # with ... as f 上下文管理器：
        # - 自动管理文件句柄，无需手动调用 f.close()；
        # - 即使写入过程中报错，也会自动关闭文件，避免文件句柄泄露；
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(test_content.strip())
        print(f"✅ 自动创建测试文档：{file_path}")

    # 加载并切分文档
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()

    # 中文文本切分配置 定义「文本切分的分隔符列表」，切分器会按列表优先级，从文本中寻找这些分隔符，把长文本拆分成符合 chunk_size 要求的小文本块（chunk）。
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # 每个文本块最大字符数
        chunk_overlap=50,  # 块之间重叠字符数（保证上下文连贯）
        separators=["\n\n", "\n", "。", "！", "？", "，", "、"]  # 中文分隔符
    )
    # split_docs是一个列表
    split_docs = splitter.split_documents(documents)

    # 提取有效文本块 列表推导式for doc in split_docs用来清洗列表
    text_chunks = [doc.page_content.strip() for doc in split_docs if doc.page_content.strip()]
    print(f"✅ 文档切分完成，共生成 {len(text_chunks)} 个文本块")
    return text_chunks


def init_chroma_db(text_chunks: List[str]) -> chromadb.Collection:
    """
    初始化 Chroma 向量库，存入阿里云百炼生成的嵌入向量
    :param text_chunks: 切分后的文本块列表
    :return: Chroma 集合对象
    """
    # 初始化本地持久化向量库
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    collection = client.get_or_create_collection(name="aliyun_rag_docs")

    # 清空旧数据（避免重复）
    if collection.count() > 0:
        collection.delete(ids=[str(i) for i in range(collection.count())])

    # 批量生成嵌入向量并入库 三元组
    embeddings = []
    valid_texts = []
    valid_ids = []
    # enumerate(text_chunks)：Python 内置的「枚举函数」，作用是遍历列表时同时获取索引和元素
    for idx, text in enumerate(text_chunks):
        embedding = get_embedding_by_aliyun(text)
        if embedding:  # 只保留生成成功的向量
            embeddings.append(embedding)
            valid_texts.append(text)
            valid_ids.append(str(idx))

    # 存入向量库
    if valid_texts:
        collection.add(
            ids=valid_ids,
            documents=valid_texts,
            embeddings=embeddings
        )
        print(f"✅ 向量库初始化完成，存入 {len(valid_texts)} 个文本块")
    else:
        print("⚠️ 无有效文本块存入向量库")

    return collection

# top_k默认值3 top_k: int = 3
def retrieve_relevant_docs(collection: chromadb.Collection, query: str, top_k: int = 3) -> List[str]:
    """
    检索与问题最相关的文本块
    :param collection: Chroma 集合对象
    :param query: 用户问题
    :param top_k: 返回最相关的前k个文本块
    :return: 相关文本块列表
    """
    # 生成问题的嵌入向量
    query_embedding = get_embedding_by_aliyun(query)
    if not query_embedding:
        print("❌ 问题向量生成失败，无法检索")
        return []

    # 向量相似度检索 接收「用户提问的嵌入向量」和「要返回的相似结果数量」，通过余弦相似度算法计算提问向量与 Collection 中所有向量的相似度，返回相似度最高的 top_k 个结果
    # results 是 Chroma 返回的一个字典对象，字典的本质是「键值对（key-value）」的无序集合
    # results = {
    #     "ids": List[List[str]],  # 匹配到的文本块ID列表（二维）
    #     "embeddings": Optional[List[List[List[float]]]],  # 匹配到的向量（默认不返回）
    #     "documents": List[List[str]],  # 匹配到的原始文本块（二维）
    #     "metadatas": Optional[List[List[Optional[Dict]]]],  # 元数据（二维）
    #     "distances": Optional[List[List[float]]]  # 相似度距离（二维）
    # }
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    # 提取检索结果
    relevant_docs = results["documents"][0] if results["documents"] else []
    print(f"✅ 检索到 {len(relevant_docs)} 个相关文本块")
    return relevant_docs


def get_answer_by_aliyun(query: str, relevant_docs: List[str]) -> str:
    """
    调用阿里云百炼大模型（qwen-turbo）生成基于检索结果的回答
    :param query: 用户问题
    :param relevant_docs: 检索到的相关文本块
    :return: 生成的回答
    """
    # 构建 RAG Prompt 模板（核心：限定回答仅基于上下文）
    prompt_template = """
    请严格基于以下上下文信息回答用户问题，遵守以下规则：
    1. 只使用上下文提供的信息，不编造任何未提及的内容；
    2. 用简洁、清晰的中文回答，避免冗余；
    3. 如果上下文没有相关信息，直接回答“无法从文档中找到相关答案”。
    
    上下文信息：
    {context}
    
    用户问题：{query}
    """

    # 拼接上下文 join() 是 Python 字符串的核心方法，作用是「用指定分隔符拼接可迭代对象（如列表）的所有元素」
    context = "\n\n".join(relevant_docs) if relevant_docs else "无相关信息"
    # 通过「关键字参数」把变量值填充到模板的对应占位符中
    final_prompt = prompt_template.format(context=context, query=query)

    try:
        # 调用阿里云百炼大模型
        completion = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.1,  # 降低随机性，保证回答精准
            timeout=30
        )
        # 解析回答
        answer = completion.choices[0].message.content.strip()
        return answer
    except Exception as e:
        print(f"❌ 调用阿里云百炼大模型失败：{e}")
        return f"回答生成失败：{str(e)}"


# ===================== 完整 RAG 问答流程 =====================
def aliyun_rag_qa(query: str) -> Dict[str, any]:
    """
    端到端的 RAG 问答流程
    :param query: 用户问题
    :return: 包含问题、回答、检索文档的字典
    """
    # 步骤1：加载并切分文档
    text_chunks = load_and_split_document(DOCUMENT_PATH)

    # 步骤2：初始化向量库
    collection = init_chroma_db(text_chunks)

    # 步骤3：检索相关文档
    relevant_docs = retrieve_relevant_docs(collection, query)

    # 步骤4：生成回答
    answer = get_answer_by_aliyun(query, relevant_docs)

    # 返回结果
    return {
        "query": query,
        "answer": answer,
        "relevant_documents": relevant_docs
    }


# ===================== 测试运行 =====================
if __name__ == "__main__":
    # 前置检查：确保 API Key 和 Base URL 配置正确
    if not os.getenv("API_KEY") or not os.getenv("BASE_URL"):
        print("❌ 请在 .env 文件中配置 API_KEY 和 BASE_URL！")
        exit(1)

    # 启动问答交互
    print("=== 阿里云百炼 text-embedding-v4 RAG 问答系统 ===")
    while True:
        query = input("\n请输入你的问题（输入 exit 退出）：").strip()
        if not query:
            print("⚠️ 请输入有效问题！")
            continue
        if query.lower() == "exit":
            print("👋 退出问答系统")
            break

        # 执行 RAG 流程
        result = aliyun_rag_qa(query)

        # 输出结果
        print("\n=== 回答结果 ===")
        print(f"问题：{result['query']}")
        print(f"回答：{result['answer']}")

        # 输出检索到的参考文档（可选）
        if result["relevant_documents"]:
            print("\n=== 参考文档 ===")
            for idx, doc in enumerate(result["relevant_documents"], 1):
                print(f"{idx}. {doc}")
        print("-" * 80)