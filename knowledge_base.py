import chromadb
from chromadb.utils import embedding_functions
import os

# 定义数据库存储的路径
CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), ".chroma_db")

# 使用 sentence-transformers 默认的模型，它会全自动下载并缓存在本地
# 这里使用更轻量级和较快速的 "all-MiniLM-L6-v2"
default_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

def get_or_create_collection():
    """
    初始化 Chroma 向量数据库，并默认灌入一些品牌的 Guidelines。
    如果库已经存在就不会重复注入了。
    """
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    
    # 获取或者创建集合 (Collection)
    collection = client.get_or_create_collection(
        name="brand_guidelines",
        embedding_function=default_ef
    )
    
    # 判断一下如果库是空的，我们塞一些“历史爆款经验”和“品牌调性”进去测试
    if collection.count() == 0:
        print("📦 首次运行：检测到本地知识库为空，正在向 ChromaDB 注入品牌知识库数据 (RAG)...")
        documents = [
            "【历史爆款参考】面向开发者的宣传文案：兄弟们！又熬夜改 Bug 呢？这次我们上线了宇宙最强 AI 助手，帮你把代码直接写到天上！重点：切忌正经，要用极其接地气的‘极客口吻’和大家打招呼。",
            "【历史爆款参考】小红书画风爆款文案：家人们谁懂啊！今天发现了一个神仙打工工具，摸鱼必备！重点：多用Emoji，多用‘绝绝子’、‘打工人’等热词。",
            "【品牌设计规范】科技感视频配图要求：不要过于卡通。要求使用赛博朋克（Cyberpunk）、全息投影（Holographic）、霓虹灯光（Neon lights）、暗色背景（Dark background）的冷酷视觉。",
            "【品牌设计规范】亲和力图文配图要求：要求画面清晰明亮，多用马卡龙色系（Macaron colors），3D 粘土风格（3D clay style），可爱治愈系（Cute and healing）。"
        ]
        
        # 给每条知识打个 ID
        ids = [f"knowledge_{i}" for i in range(len(documents))]
        
        # 存进去！底层会自动去算这四段话的 Embedding(向量积)
        collection.add(
            documents=documents,
            ids=ids
        )
        print("✅ 知识库注入完成！")
        
    return collection

def retrieve_knowledge(query: str, n_results: int = 1) -> str:
    """
    提供给 Agent 使用的检索函数。
    给出一个查询词，去 ChromaDB 里捞出最相关的 n 条品牌经验。
    """
    collection = get_or_create_collection()
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    # 把检索到的文本拼接成一块大字符串
    if results and len(results['documents']) > 0 and len(results['documents'][0]) > 0:
        fetched_docs = results['documents'][0]
        # 拼接成参考上下文
        context = "\n".join(fetched_docs)
        return context
    
    return "无特殊品牌限制"

# 临时测试一下检索功能是否正常
if __name__ == "__main__":
    test_context = retrieve_knowledge("我想发一篇面对打工人的小红书搞笑推文", n_results=1)
    print("\n[检索测试结果]:\n", test_context)
