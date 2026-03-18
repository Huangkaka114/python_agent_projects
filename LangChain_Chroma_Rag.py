# -*- coding: utf-8 -*-
import sys

sys.stdin.reconfigure(encoding='utf-8')

import os
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

# LangChain 官方标准导入
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma

# ===================== 加载环境变量 =====================
load_dotenv()

# ===================== 配置 =====================
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
EMBEDDING_MODEL = "text-embedding-v4"
LLM_MODEL = "qwen-turbo"
VECTOR_DB_PATH = "./aliyun_rag_chroma"
DOCUMENT_PATH = "doc/news_content.txt"


# ===================== 1. 官方标准：自定义 Embeddings =====================
class AliyunEmbeddings(Embeddings):
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        if not text.strip():
            return []
        try:
            res = self.client.embeddings.create(model=EMBEDDING_MODEL, input=text.strip())
            return res.data[0].embedding
        except Exception as e:
            print(f"嵌入失败: {e}")
            return []


# ===================== 2. 官方标准：文档加载与切分 =====================
def load_and_split() -> List[Document]:
    os.makedirs(os.path.dirname(DOCUMENT_PATH), exist_ok=True)
    if not os.path.exists(DOCUMENT_PATH):
        content = """
        通义千问（Qwen）是阿里云研发的大语言模型，支持多轮对话、文本生成、知识问答等场景。
        阿里云百炼（Model Studio）是一站式大模型开发平台，提供嵌入模型、大语言模型等多种能力。
        text-embedding-v4 是阿里云百炼推出的轻量级文本嵌入模型，输出768维向量，适合RAG场景。
        RAG（检索增强生成）的核心是先检索相关文档，再基于文档生成回答，能有效解决大模型幻觉问题。
        使用阿里云百炼构建RAG的步骤：1.文档切分 2.生成嵌入向量 3.存入向量库 4.检索 5.生成回答。
        """
        with open(DOCUMENT_PATH, "w", encoding="utf-8") as f:
            f.write(content.strip())

    loader = TextLoader(DOCUMENT_PATH, encoding="utf-8")
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", "，", "、"]
    )
    return splitter.split_documents(docs)


# ===================== 3. 向量库 =====================
def get_vectorstore():
    embedding = AliyunEmbeddings()
    docs = load_and_split()
    return Chroma.from_documents(
        documents=docs,
        embedding=embedding,
        persist_directory=VECTOR_DB_PATH
    )


# ===================== 4. 检索器 =====================
def get_retriever(k: int = 3):
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever(search_kwargs={"k": k})


# ===================== 5. Prompt 模板 =====================
PROMPT = PromptTemplate(
    input_variables=["context", "query"],
    template="""
请严格基于以下上下文信息回答用户问题：
1. 只使用上下文提供的信息，不编造内容。
2. 简洁清晰回答。
3. 无相关信息则回复：无法从文档中找到相关答案。

上下文：
{context}

问题：{query}
""",
)


# ===================== 6. LLM 调用 =====================
class AliyunLLM:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    def invoke(self, prompt: str) -> str:
        try:
            res = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            return f"调用失败：{str(e)}"


# ===================== 7. RAG 主流程 =====================
def aliyun_rag_qa(query: str) -> Dict:
    retriever = get_retriever()

    # ===================== 修复在这里！=====================
    # 旧：docs = retriever.get_relevant_documents(query)
    # 新：
    docs = retriever.invoke(query)
    # ======================================================

    context = "\n".join([d.page_content for d in docs])
    prompt = PROMPT.format(context=context, query=query)
    llm = AliyunLLM()
    answer = llm.invoke(prompt)

    return {
        "query": query,
        "answer": answer,
        "relevant_documents": [d.page_content for d in docs]
    }


# ===================== 运行 =====================
if __name__ == "__main__":
    if not API_KEY or not BASE_URL:
        print("❌ 请配置 .env 文件")
        exit(1)

    print("=== 阿里云百炼 RAG 问答系统（LangChain 官方标准）===")
    while True:
        query = input("\n请输入问题（exit 退出）：").strip()
        if not query: continue
        if query.lower() == "exit": break

        res = aliyun_rag_qa(query)
        print("\n🤖 回答：", res["answer"])

        if res["relevant_documents"]:
            print("\n📚 参考文档：")
            for i, d in enumerate(res["relevant_documents"], 1):
                print(f"{i}. {d}")