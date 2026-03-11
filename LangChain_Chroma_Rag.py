from re import search
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA
import os
from dotenv import load_dotenv
# 新增本地Embedding导入
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

# 加载文档
loader = TextLoader("doc/news_content.txt",encoding="utf-8")
documents = loader.load()

# 切分文本
splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)
texts = splitter.split_documents(documents)
print(f"✅ 切分完成，共 {len(texts)} 个文本块")

# 向量&库（本地Embedding，无API依赖）
embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)
texts_content = [doc.page_content for doc in texts]
embeddings = embedding_model.embed_documents(texts_content)
print(f"✅ 本地Embedding生成成功，共{len(embeddings)}个向量")
db = Chroma(
    collection_name="news",
    embedding_function=None,
    persist_directory="./chroma_db"
)
db.add_texts(texts=texts_content, embeddings=embeddings)

# 大模型
llm = ChatOpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
    model="deepseek-chat",
    temperature = 0.3
)

# Rag链
qa_chain = RetrievalQA.from_chain_type(
    llm = llm,
    chain_type="stuff",
    retriever = db.as_retriever(search_kwargs={"k":3}),
    return_source_document=True
)

if __name__ == "__main__":
    print("=== RAG 本地文档问答机器人 ===")
    while True:
        question = input("请输入问题（输入 exit 退出）：")
        if question == "exit":
            break
        result = qa_chain.invoke({"query": question})
        print("\n【回答】")
        print(result["result"])
        print("-"*50)