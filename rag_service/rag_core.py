"""
RAG服务核心模块
=================

本模块是RAG（检索增强生成）服务的核心实现，提供以下主要功能：

主要功能：
---------
1. 文档向量化与存储：支持多种文档格式的文本提取和向量化
2. 智能检索：基于语义相似度的文档检索
3. 生成回答：结合检索内容和大语言模型生成准确回答
4. 在线/离线模式：支持网络环境和离线环境的自动切换

技术架构：
---------
- LLM: 使用 Ollama 作为大语言模型服务
- 向量存储: 使用 ChromaDB 作为向量数据库
- 嵌入模型: 支持 HuggingFace 在线模型和离线 TF-IDF 方案
- 索引框架: 使用 LlamaIndex 构建检索索引

支持的文档格式：
-------------
- 文本文件 (.txt)
- Markdown 文件 (.md)
- PDF 文件 (.pdf，需安装 pypdf)
- Word 文档 (.docx，计划支持)

部署模式：
---------
- 在线模式：需要网络连接，使用 HuggingFace 嵌入模型
- 离线模式：无网络连接时自动切换，使用 TF-IDF 向量化方案


创建日期: 2025年7月
版本: 1.0

模块结构：
========

1. 依赖导入模块
   - 标准库导入
   - 第三方库导入（LlamaIndex, ChromaDB等）
   - 版本兼容性处理

2. RAGService 核心类
   - __init__: 服务初始化和配置
   - _setup_* 方法: 各组件初始化
   - add_documents: 文档添加和向量化
   - query: 智能问答查询
   - _offline_* 方法: 离线模式处理
   - 工具方法: 状态检查、索引管理等

3. 全局服务管理
   - 单例模式实现
   - 环境变量配置
   - 统一访问入口

使用示例：
========

```python
# 获取服务实例
rag = get_rag_service()

# 添加文档
rag.add_documents(['path/to/document.txt'])

# 查询问答
result = rag.query("您的问题")
print(result['answer'])
```
"""

import os
import logging
from typing import List, Optional
from pathlib import Path

# 依赖库导入模块
# ===============
# 尝试导入 LlamaIndex 相关组件，支持新旧版本兼容

try:
    # 尝试新版本导入 (llama-index >= 0.9.0)
    # 新版本将核心组件移到了 llama_index.core 模块下
    from llama_index.core import (
        VectorStoreIndex, 
        SimpleDirectoryReader, 
        Settings,
        StorageContext
    )
    from llama_index.core.node_parser import SimpleNodeParser
    from llama_index.llms.ollama import Ollama
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.vector_stores.chroma import ChromaVectorStore
except ImportError:
    # 回退到旧版本导入 (llama-index < 0.9.0)
    # 旧版本的组件直接在 llama_index 模块下
    try:
        from llama_index import (
            VectorStoreIndex, 
            SimpleDirectoryReader, 
            ServiceContext,
            StorageContext
        )
        from llama_index.node_parser import SimpleNodeParser
        from llama_index.llms import Ollama
        from llama_index.embeddings import HuggingFaceEmbedding
        from llama_index.vector_stores import ChromaVectorStore
        Settings = None  # 旧版本使用ServiceContext而不是Settings
    except ImportError as e:
        print(f"导入LlamaIndex失败: {e}")
        print("请先运行: pip install llama-index")
        raise

import chromadb
# ChromaDB 配置导入
from chromadb.config import Settings as ChromaSettings

# 日志配置模块
# ============
# 配置日志系统，用于记录 RAG 服务的运行状态和调试信息
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    """
    RAG（检索增强生成）服务类
    ========================
    
    这是 RAG 系统的核心服务类，提供完整的文档检索和问答功能。
    
    主要职责：
    --------
    1. 管理大语言模型（LLM）连接和配置
    2. 处理文档的向量化和存储
    3. 实现语义检索和答案生成
    4. 支持在线和离线两种运行模式
    5. 提供向量数据库的管理功能
    
    架构组件：
    ---------
    - LLM: Ollama 服务，负责文本生成
    - 嵌入模型: HuggingFace 模型或离线 TF-IDF
    - 向量存储: ChromaDB 持久化向量数据库
    - 索引系统: LlamaIndex 检索框架
    
    使用场景：
    ---------
    - 企业知识库问答
    - 文档智能检索
    - 内容推荐系统
    - 客服机器人
    """
    
    def __init__(self, 
                 ollama_base_url: str = "http://localhost:11434",
                 model_name: str = "maoniang:latest",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 documents_path: str = "./documents",
                 vector_store_path: str = "./vector_store",
                 chunk_size: int = 1024,
                 chunk_overlap: int = 20,
                 top_k: int = 5):
        """
        初始化 RAG 服务
        
        参数说明：
        --------
        ollama_base_url: str
            Ollama 服务的基础 URL 地址
        model_name: str  
            使用的大语言模型名称
        embedding_model: str
            文本嵌入模型名称
        documents_path: str
            文档存储目录路径
        vector_store_path: str
            向量数据库存储路径
        chunk_size: int
            文档分块大小（字符数）
        chunk_overlap: int
            文档分块重叠大小
        top_k: int
            检索时返回的相关文档数量
        """
        
        # 存储配置参数
        self.ollama_base_url = ollama_base_url
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.documents_path = Path(documents_path)
        self.vector_store_path = Path(vector_store_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        self.offline_mode = False  # 离线模式标志，自动检测网络状态
        
        # 组件初始化序列
        # ==============
        # 按依赖关系依次初始化各个组件
        self._setup_llm()           # 1. 初始化大语言模型
        self._setup_embedding()     # 2. 初始化嵌入模型
        self._setup_vector_store()  # 3. 初始化向量存储
        self._setup_index()         # 4. 初始化检索索引
        
    def _setup_llm(self):
        """
        大语言模型初始化模块
        ===================
        
        功能说明：
        --------
        - 连接到 Ollama 服务
        - 配置模型参数和超时设置
        - 验证模型可用性
        
        异常处理：
        --------
        - 连接失败时抛出异常
        - 记录详细的错误信息
        """
        try:
            # 创建 Ollama 客户端实例
            self.llm = Ollama(
                model=self.model_name,
                base_url=self.ollama_base_url,
                request_timeout=60.0  # 设置 60 秒超时
            )
            logger.info(f"LLM设置完成: {self.model_name}")
        except Exception as e:
            logger.error(f"LLM设置失败: {e}")
            raise
    
    def _setup_embedding(self):
        """
        嵌入模型初始化模块
        =================
        
        功能说明：
        --------
        - 自动检测网络连接状态
        - 在线模式：使用 HuggingFace 预训练模型
        - 离线模式：使用 TF-IDF 向量化方案
        - 智能缓存管理
        
        模式切换逻辑：
        -----------
        1. 首先尝试网络连接检测
        2. 有网络：加载 HuggingFace 模型
        3. 无网络或加载失败：切换到离线 TF-IDF 模式
        4. 支持模型缓存复用
        
        离线方案特点：
        -----------
        - 使用 scikit-learn TF-IDF 向量化
        - 支持中文分词（可选 jieba）
        - 自适应词汇表构建
        - 与在线模式兼容的接口
        """
        # 网络连接检测子模块
        def check_internet_connection():
            """
            检查网络连接状态
            
            返回值：
            ------
            bool: True 表示网络可用，False 表示无网络
            """
            try:
                import requests
                response = requests.get("https://hf-mirror.com", timeout=3)
                return response.status_code == 200
            except:
                return False
        
        has_internet = check_internet_connection()
        logger.info(f"网络连接状态: {'可用' if has_internet else '不可用'}")
        
        if has_internet:
            try:
                # 设置HuggingFace镜像环境变量
                import os
                os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
                
                # 使用配置的缓存路径
                cache_path = os.path.join(os.getcwd(), "embeddings_cache")
                
                # 有网络时尝试在线嵌入模型
                logger.info(f"尝试加载在线嵌入模型: {self.embedding_model}")
                self.embed_model = HuggingFaceEmbedding(
                    model_name=self.embedding_model,
                    cache_folder=cache_path,
                    trust_remote_code=True
                )
                logger.info(f"嵌入模型设置完成: {self.embedding_model}")
                self.offline_mode = False
                return
            except Exception as e:
                logger.warning(f"在线嵌入模型加载失败: {e}")
                logger.info("尝试使用本地缓存模型...")
                
                # 尝试使用已缓存的模型
                try:
                    cache_path = os.path.join(os.getcwd(), "embeddings_cache")
                    if os.path.exists(cache_path):
                        self.embed_model = HuggingFaceEmbedding(
                            model_name=self.embedding_model,
                            cache_folder=cache_path,
                            trust_remote_code=True
                        )
                        logger.info(f"使用缓存的嵌入模型: {self.embedding_model}")
                        self.offline_mode = False
                        return
                except Exception as cache_error:
                    logger.warning(f"缓存模型加载失败: {cache_error}")
        
        # 无网络或在线模式失败，切换到离线模式
        logger.info("切换到离线模式...")
        
        try:
            # 使用离线TF-IDF方案
            from sklearn.feature_extraction.text import TfidfVectorizer
            try:
                import jieba
                has_jieba = True
            except ImportError:
                has_jieba = False
                logger.warning("jieba不可用，将使用简单分词")
            
            # 创建自定义的离线嵌入类
            class OfflineEmbedding:
                def __init__(self):
                    if has_jieba:
                        self.vectorizer = TfidfVectorizer(
                            max_features=1000,
                            ngram_range=(1, 2),
                            tokenizer=self._chinese_tokenizer
                        )
                    else:
                        self.vectorizer = TfidfVectorizer(
                            max_features=1000,
                            ngram_range=(1, 2)
                        )
                    self.is_fitted = False
                    cache_dir = os.path.join(os.getcwd(), "embeddings_cache")
                    self.vocab_cache_path = Path(cache_dir) / "tfidf_vocab.pkl"
                    self.vocab_cache_path.parent.mkdir(exist_ok=True)
                
                def _chinese_tokenizer(self, text):
                    """中文分词器"""
                    try:
                        import jieba
                        return list(jieba.cut(text))
                    except:
                        # 如果jieba不可用，使用简单的空格分词
                        return text.split()
                
                def _load_existing_documents(self):
                    """加载现有文档来训练向量化器"""
                    try:
                        # 尝试从ChromaDB加载现有文档
                        collection_name = "rag_documents"
                        vector_store_path = Path("./vector_store")
                        chroma_client = chromadb.PersistentClient(
                            path=str(vector_store_path),
                            settings=ChromaSettings(anonymized_telemetry=False)
                        )
                        
                        collection = chroma_client.get_collection(collection_name)
                        result = collection.get()
                        
                        if result['documents']:
                            logger.info(f"加载了 {len(result['documents'])} 个现有文档用于训练向量化器")
                            return result['documents']
                    except Exception as e:
                        logger.warning(f"无法加载现有文档: {e}")
                    
                    # 如果没有现有文档，使用默认文档
                    return [
                        "这是一个测试文档",
                        "RAG检索增强生成技术",
                        "向量数据库存储文档",
                        "人工智能自然语言处理"
                    ]
                
                def get_text_embedding(self, text):
                    """获取文本嵌入"""
                    if not self.is_fitted:
                        # 加载现有文档来训练向量化器
                        training_docs = self._load_existing_documents()
                        training_docs.append(text)  # 添加当前查询文本
                        
                        self.vectorizer.fit(training_docs)
                        self.is_fitted = True
                        logger.info(f"TF-IDF向量化器训练完成，词汇表大小: {len(self.vectorizer.vocabulary_)}")
                    
                    vector = self.vectorizer.transform([text])
                    return vector.toarray()[0].tolist()
                
                def get_text_embedding_batch(self, texts):
                    """批量获取文本嵌入"""
                    if not self.is_fitted:
                        # 使用提供的文本训练
                        training_docs = self._load_existing_documents()
                        training_docs.extend(texts)
                        
                        self.vectorizer.fit(training_docs)
                        self.is_fitted = True
                        logger.info(f"TF-IDF向量化器训练完成，词汇表大小: {len(self.vectorizer.vocabulary_)}")
                    
                    vectors = self.vectorizer.transform(texts)
                    return [vec.tolist() for vec in vectors.toarray()]
            
            self.embed_model = OfflineEmbedding()
            self.offline_mode = True
            logger.info("离线嵌入模型设置完成（使用TF-IDF）")
            
        except ImportError as e:
            logger.error("离线模式需要 scikit-learn，请安装：pip install scikit-learn")
            raise Exception(f"离线模式依赖缺失: {e}")
        except Exception as offline_error:
            logger.error(f"离线嵌入模型设置失败: {offline_error}")
            raise
    
    def _setup_vector_store(self):
        """
        向量存储初始化模块
        =================
        
        功能说明：
        --------
        - 配置 ChromaDB 持久化客户端
        - 创建或连接向量集合
        - 设置向量存储包装器
        
        存储特性：
        --------
        - 持久化存储：数据保存到磁盘
        - 禁用遥测：保护隐私
        - 自动集合管理：智能创建和连接
        """
        try:
            # 创建ChromaDB客户端，禁用遥测
            chroma_settings = ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
            
            chroma_client = chromadb.PersistentClient(
                path=str(self.vector_store_path),
                settings=chroma_settings
            )
            
            # 获取或创建集合
            collection_name = "rag_documents"
            try:
                chroma_collection = chroma_client.get_collection(collection_name)
                logger.info(f"找到现有集合: {collection_name}")
            except Exception:
                chroma_collection = chroma_client.create_collection(collection_name)
                logger.info(f"创建新集合: {collection_name}")
            
            # 创建向量存储
            self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            logger.info("向量存储设置完成")
        except Exception as e:
            logger.error(f"向量存储设置失败: {e}")
            raise
    
    def _setup_index(self):
        """
        检索索引初始化模块
        =================
        
        功能说明：
        --------
        - 配置 LlamaIndex 检索系统
        - 支持新旧版本兼容性
        - 创建查询引擎
        
        版本兼容：
        --------
        - 新版本：使用 Settings 全局配置
        - 旧版本：使用 ServiceContext 上下文
        
        索引管理：
        --------
        - 尝试加载现有索引
        - 创建新索引（如果不存在）
        - 配置查询引擎参数
        
        离线模式：
        --------
        - 离线模式下跳过 LlamaIndex 设置
        - 使用自定义检索逻辑
        """
        try:
            # 离线模式检查
            if self.offline_mode:
                logger.info("离线模式：跳过LlamaIndex索引设置")
                self.index = None
                self.query_engine = None
                return
                
            # 版本兼容配置处理
            if Settings is not None:
                # 新版本 LlamaIndex 使用 Settings 全局配置
                Settings.llm = self.llm
                Settings.embed_model = self.embed_model
                if hasattr(Settings, 'node_parser'):
                    Settings.node_parser = SimpleNodeParser.from_defaults(
                        chunk_size=self.chunk_size,
                        chunk_overlap=self.chunk_overlap
                    )
                service_context = None
            else:
                # 旧版本 LlamaIndex 使用 ServiceContext
                service_context = ServiceContext.from_defaults(
                    llm=self.llm,
                    embed_model=self.embed_model,
                    node_parser=SimpleNodeParser.from_defaults(
                        chunk_size=self.chunk_size,
                        chunk_overlap=self.chunk_overlap
                    )
                )
            
            # 创建存储上下文
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            
            # 尝试加载现有索引
            try:
                if service_context:
                    # 旧版本
                    self.index = VectorStoreIndex.from_vector_store(
                        vector_store=self.vector_store,
                        storage_context=storage_context,
                        service_context=service_context
                    )
                else:
                    # 新版本
                    self.index = VectorStoreIndex.from_vector_store(
                        vector_store=self.vector_store,
                        storage_context=storage_context
                    )
                logger.info("加载现有索引")
            except Exception:
                # 如果没有现有索引，创建空索引
                if service_context:
                    # 旧版本
                    self.index = VectorStoreIndex([], 
                                                storage_context=storage_context,
                                                service_context=service_context)
                else:
                    # 新版本
                    self.index = VectorStoreIndex([], storage_context=storage_context)
                logger.info("创建新索引")
            
            # 创建查询引擎
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=self.top_k,
                response_mode="compact"
            )
            
            logger.info("索引设置完成")
        except Exception as e:
            logger.error(f"索引设置失败: {e}")
            raise
    
    def add_documents(self, file_paths: Optional[List[str]] = None) -> bool:
        """
        文档添加模块
        ==========
        
        功能说明：
        --------
        - 支持单文件或批量文档添加
        - 自动文本提取和分块处理
        - 向量化并存储到数据库
        
        参数说明：
        --------
        file_paths: Optional[List[str]]
            指定要添加的文件路径列表，如果为 None 则处理整个文档目录
            
        返回值：
        ------
        bool: 成功返回 True，失败返回 False
        
        处理流程：
        --------
        1. 检查运行模式（在线/离线）
        2. 加载和解析文档
        3. 文本分块处理
        4. 向量化存储
        5. 更新索引
        """
        try:
            # 运行模式检查
            if self.offline_mode:
                return self._offline_add_documents(file_paths)
            
            # 文档加载处理
            if file_paths:
                # 处理指定的文件列表
                documents = []
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        reader = SimpleDirectoryReader(input_files=[file_path])
                        docs = reader.load_data()
                        documents.extend(docs)
                        logger.info(f"加载文档: {file_path}")
            else:
                # 处理整个文档目录
                if not self.documents_path.exists():
                    self.documents_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"创建文档目录: {self.documents_path}")
                    return True
                
                reader = SimpleDirectoryReader(
                    input_dir=str(self.documents_path),
                    recursive=True  # 递归处理子目录
                )
                documents = reader.load_data()
            
            # 文档验证
            if not documents:
                logger.warning("没有找到文档")
                return True
            
            # 批量添加文档到索引
            for doc in documents:
                self.index.insert(doc)
            
            logger.info(f"成功添加 {len(documents)} 个文档到索引")
            return True
            
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return False
    
    def query(self, question: str) -> dict:
        """
        智能问答查询模块
        ==============
        
        功能说明：
        --------
        - 语义检索相关文档
        - 结合 LLM 生成准确回答
        - 提供答案来源追踪
        
        参数说明：
        --------
        question: str
            用户提出的问题
            
        返回值：
        ------
        dict: 包含以下字段的响应字典
            - success: bool, 查询是否成功
            - answer: str, 生成的回答
            - sources: list, 答案来源文档信息
            - question: str, 原始问题
            - error: str, 错误信息（如果失败）
            
        查询流程：
        --------
        1. 输入验证和预处理
        2. 模式检查（在线/离线）
        3. 语义检索相关文档
        4. LLM 生成回答
        5. 源文档信息提取
        6. 结果格式化返回
        """
        try:
            # 输入验证
            if not question.strip():
                return {
                    "success": False,
                    "error": "问题不能为空"
                }
            
            logger.info(f"查询问题: {question}")
            
            # 模式路由：根据运行模式选择处理方式
            if self.offline_mode:
                return self._offline_query(question)
            
            # 在线模式：使用 LlamaIndex 完整功能
            response = self.query_engine.query(question)
            
            # 提取源文档信息用于答案追踪
            source_nodes = response.source_nodes if hasattr(response, 'source_nodes') else []
            sources = []
            for node in source_nodes:
                if hasattr(node, 'metadata') and node.metadata:
                    source_info = {
                        "file_name": node.metadata.get("file_name", "未知"),
                        "page_label": node.metadata.get("page_label", "未知"),
                        "score": getattr(node, 'score', 0.0)
                    }
                    sources.append(source_info)
            
            # 构建成功响应
            result = {
                "success": True,
                "answer": str(response),
                "sources": sources,
                "question": question
            }
            
            logger.info("查询完成")
            return result
            
        except Exception as e:
            logger.error(f"查询失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "question": question
            }
    
    def _offline_query(self, question: str) -> dict:
        """
        离线模式查询处理模块
        ==================
        
        功能说明：
        --------
        - 使用 TF-IDF 进行文档检索
        - 结合 Ollama 生成智能回答
        - 提供向量维度兼容性检查
        
        离线查询特点：
        -----------
        - 无需网络连接
        - 使用本地向量化方案
        - 智能回退机制
        - 维度匹配验证
        
        处理流程：
        --------
        1. 连接本地 ChromaDB
        2. 查询向量化
        3. 向量检索
        4. 上下文组合
        5. LLM 生成回答
        6. 结果格式化
        """
        try:
            logger.info("使用离线模式进行查询")
            
            # 从ChromaDB检索相关文档
            collection_name = "rag_documents"
            chroma_client = chromadb.PersistentClient(
                path=str(self.vector_store_path),
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            
            try:
                collection = chroma_client.get_collection(collection_name)
            except Exception:
                return {
                    "success": False,
                    "error": "没有找到文档索引，请先上传文档",
                    "question": question
                }
            
            # 查询向量化
            query_embedding = self.embed_model.get_text_embedding(question)
            
            # 检查向量维度是否匹配
            try:
                # 尝试获取集合中现有文档的信息
                existing_data = collection.get(limit=1)
                if existing_data['embeddings'] and len(existing_data['embeddings']) > 0:
                    existing_dim = len(existing_data['embeddings'][0])
                    current_dim = len(query_embedding)
                    
                    if existing_dim != current_dim:
                        logger.warning(f"向量维度不匹配：现有={existing_dim}, 当前={current_dim}，需要重建索引")
                        return {
                            "success": False,
                            "error": f"向量维度不匹配，请重建索引。现有维度：{existing_dim}，当前维度：{current_dim}",
                            "question": question,
                            "dimension_mismatch": True
                        }
            except Exception as e:
                logger.warning(f"检查向量维度失败: {e}")
            
            # 检索相关文档
            try:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=self.top_k
                )
            except Exception as e:
                error_msg = str(e)
                if "dimension" in error_msg.lower():
                    logger.error(f"向量维度不匹配错误: {error_msg}")
                    return {
                        "success": False,
                        "error": f"向量维度不匹配: {error_msg}",
                        "question": question,
                        "dimension_mismatch": True
                    }
                else:
                    raise e
            
            if not results['documents'] or not results['documents'][0]:
                return {
                    "success": False,
                    "error": "没有找到相关文档",
                    "question": question
                }
            
            # 组合检索到的文档
            context_docs = results['documents'][0]
            context = "\n\n".join(context_docs[:3])  # 取前3个最相关的
            
            # 使用Ollama生成智能回答
            try:
                # 构建提示词
                prompt = f"""基于以下文档内容，回答用户的问题。请提供准确、简洁的回答。

相关文档内容：
{context}

用户问题：{question}

请基于上述文档内容回答问题："""
                
                # 调用Ollama生成回答
                response = self.llm.complete(prompt)
                answer = str(response).strip()
                
                if not answer:
                    # 如果Ollama没有返回内容，使用模板回答
                    answer = f"基于已索引的文档，关于 '{question}' 的相关信息如下：\n\n{context}"
                
            except Exception as e:
                logger.warning(f"Ollama生成回答失败: {e}")
                # 回退到模板回答
                answer = f"基于已索引的文档，关于 '{question}' 的相关信息如下：\n\n{context}"
            
            # 构建源信息
            sources = []
            if results['metadatas'] and results['metadatas'][0]:
                for i, metadata in enumerate(results['metadatas'][0][:3]):
                    source_info = {
                        "file_name": metadata.get("file_name", f"文档_{i+1}"),
                        "page_label": metadata.get("page_label", "未知"),
                        "score": 1 - results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.8
                    }
                    sources.append(source_info)
            
            return {
                "success": True,
                "answer": answer,
                "sources": sources,
                "question": question,
                "mode": "offline"
            }
            
        except Exception as e:
            logger.error(f"离线查询失败: {e}")
            return {
                "success": False,
                "error": f"离线查询失败: {str(e)}",
                "question": question
            }
    
    def _offline_add_documents(self, file_paths: Optional[List[str]] = None) -> bool:
        """
        离线模式文档添加模块
        ==================
        
        功能说明：
        --------
        - 无网络环境下的文档处理
        - 使用简单文本提取方案
        - TF-IDF 向量化和存储
        
        处理流程：
        --------
        1. 扫描文档文件列表
        2. 简单文本提取
        3. 文本分块处理
        4. TF-IDF 向量化
        5. 存储到 ChromaDB
        
        支持格式：
        --------
        - .txt 文本文件
        - .md Markdown 文件
        - .pdf PDF 文件（需 pypdf）
        - .docx Word 文档（计划支持）
        """
        try:
            logger.info("离线模式：添加文档")
            
            # 获取要处理的文件列表
            files_to_process = []
            
            if file_paths:
                files_to_process = [f for f in file_paths if os.path.exists(f)]
            else:
                # 扫描文档目录
                if not self.documents_path.exists():
                    self.documents_path.mkdir(parents=True, exist_ok=True)
                    return True
                
                for file_path in self.documents_path.rglob("*"):
                    if file_path.is_file() and file_path.suffix.lower() in ['.txt', '.md', '.pdf', '.docx']:
                        files_to_process.append(str(file_path))
            
            if not files_to_process:
                logger.warning("没有找到要处理的文档")
                return True
            
            # 处理每个文件
            collection_name = "rag_documents"
            chroma_client = chromadb.PersistentClient(
                path=str(self.vector_store_path),
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            
            try:
                collection = chroma_client.get_collection(collection_name)
            except Exception:
                collection = chroma_client.create_collection(collection_name)
            
            doc_count = 0
            for file_path in files_to_process:
                try:
                    # 简单的文本提取
                    text_content = self._extract_text_simple(file_path)
                    
                    if not text_content.strip():
                        continue
                    
                    # 简单的文本分块
                    chunks = self._split_text_simple(text_content, self.chunk_size, self.chunk_overlap)
                    
                    # 为每个块生成嵌入并存储
                    for i, chunk in enumerate(chunks):
                        if len(chunk.strip()) < 10:  # 跳过太短的块
                            continue
                        
                        doc_id = f"{Path(file_path).stem}_{i}"
                        embedding = self.embed_model.get_text_embedding(chunk)
                        
                        collection.add(
                            embeddings=[embedding],
                            documents=[chunk],
                            metadatas=[{
                                "file_name": Path(file_path).name,
                                "file_path": file_path,
                                "chunk_id": i
                            }],
                            ids=[doc_id]
                        )
                        doc_count += 1
                    
                    logger.info(f"处理文档: {Path(file_path).name}")
                    
                except Exception as e:
                    logger.warning(f"处理文档失败 {file_path}: {e}")
                    continue
            
            logger.info(f"离线模式：成功添加 {doc_count} 个文档块")
            return True
            
        except Exception as e:
            logger.error(f"离线添加文档失败: {e}")
            return False
    
    def _extract_text_simple(self, file_path: str) -> str:
        """
        简单文本提取模块
        ==============
        
        功能说明：
        --------
        - 从各种文件格式中提取纯文本
        - 离线模式专用，无需复杂依赖
        
        支持格式：
        --------
        - .txt/.md: 直接读取文本内容
        - .pdf: 使用 pypdf 提取（可选）
        - 其他格式: 提示不支持
        
        参数说明：
        --------
        file_path: str
            待提取的文件路径
            
        返回值：
        ------
        str: 提取的文本内容，失败时返回空字符串
        """
        try:
            file_path = Path(file_path)
            
            if file_path.suffix.lower() in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif file_path.suffix.lower() == '.pdf':
                # 如果有pypdf，尝试使用
                try:
                    import pypdf
                    with open(file_path, 'rb') as f:
                        reader = pypdf.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text() + "\n"
                        return text
                except ImportError:
                    logger.warning(f"无法处理PDF文件 {file_path}，请安装pypdf")
                    return ""
            else:
                logger.warning(f"不支持的文件格式: {file_path.suffix}")
                return ""
                
        except Exception as e:
            logger.error(f"文本提取失败 {file_path}: {e}")
            return ""
    
    def _split_text_simple(self, text: str, chunk_size: int = 1024, overlap: int = 20) -> List[str]:
        """
        简单文本分块模块
        ==============
        
        功能说明：
        --------
        - 将长文本分割成适合向量化的块
        - 智能边界检测，避免截断句子
        - 支持重叠分块，保持上下文连续性
        
        分块策略：
        --------
        - 优先在句号、换行符处分割
        - 保持指定的重叠区域
        - 过滤空白和过短的块
        
        参数说明：
        --------
        text: str
            待分块的原始文本
        chunk_size: int
            每个块的最大字符数
        overlap: int
            块间重叠的字符数
            
        返回值：
        ------
        List[str]: 分块后的文本列表
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # 尝试在句号或换行符处切分
            if end < len(text):
                # 向后查找合适的分割点
                for i in range(min(100, chunk_size - end)):
                    if text[end - i] in '.。\n':
                        end = end - i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def get_document_count(self) -> int:
        """
        文档数量统计模块
        ==============
        
        功能说明：
        --------
        - 获取向量数据库中的文档数量
        - 用于系统状态监控
        
        返回值：
        ------
        int: 数据库中存储的文档数量
        """
        try:
            # 通过向量存储获取文档数量
            collection = self.vector_store._collection
            return collection.count()
        except Exception as e:
            logger.error(f"获取文档数量失败: {e}")
            return 0
    
    def clear_index(self) -> bool:
        """
        索引清理模块
        ==========
        
        功能说明：
        --------
        - 完全清空向量数据库
        - 重新初始化索引系统
        - 重置所有缓存状态
        
        使用场景：
        --------
        - 重新构建知识库
        - 清理损坏的索引
        - 重置系统状态
        
        操作流程：
        --------
        1. 删除现有 ChromaDB 集合
        2. 重新创建空集合
        3. 重新初始化索引
        4. 重置离线模型状态
        
        返回值：
        ------
        bool: 清理成功返回 True，失败返回 False
        """
        try:
            logger.info("开始清空索引...")
            
            # 获取ChromaDB客户端和集合
            collection_name = "rag_documents"
            chroma_client = chromadb.PersistentClient(
                path=str(self.vector_store_path),
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            
            try:
                # 删除现有集合
                chroma_client.delete_collection(collection_name)
                logger.info(f"已删除集合: {collection_name}")
            except Exception as e:
                logger.warning(f"删除集合失败: {e}")
            
            try:
                # 重新创建集合
                chroma_collection = chroma_client.create_collection(collection_name)
                logger.info(f"重新创建集合: {collection_name}")
                
                # 更新向量存储引用
                self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
                
                # 如果不是离线模式，重新设置索引
                if not self.offline_mode and self.index is not None:
                    storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
                    
                    if Settings is not None:
                        # 新版本
                        self.index = VectorStoreIndex([], storage_context=storage_context)
                    else:
                        # 旧版本 - 需要service_context
                        from llama_index.node_parser import SimpleNodeParser
                        try:
                            from llama_index import ServiceContext
                            service_context = ServiceContext.from_defaults(
                                llm=self.llm,
                                embed_model=self.embed_model,
                                node_parser=SimpleNodeParser.from_defaults(
                                    chunk_size=self.chunk_size,
                                    chunk_overlap=self.chunk_overlap
                                )
                            )
                            self.index = VectorStoreIndex([], 
                                                        storage_context=storage_context,
                                                        service_context=service_context)
                        except ImportError:
                            # 如果导入失败，使用新版本方式
                            self.index = VectorStoreIndex([], storage_context=storage_context)
                    
                    # 重新创建查询引擎
                    self.query_engine = self.index.as_query_engine(
                        similarity_top_k=self.top_k,
                        response_mode="compact"
                    )
                
                # 重置TF-IDF向量化器（如果在离线模式）
                if self.offline_mode:
                    self.embed_model.is_fitted = False
                    logger.info("已重置TF-IDF向量化器")
                
            except Exception as e:
                logger.error(f"重新创建集合失败: {e}")
                return False
            
            logger.info("索引已清空并重新初始化")
            return True
        except Exception as e:
            logger.error(f"清空索引失败: {e}")
            return False
    
    def health_check(self) -> dict:
        """
        系统健康检查模块
        ==============
        
        功能说明：
        --------
        - 检查各组件运行状态
        - 验证服务连接性
        - 提供系统诊断信息
        
        检查项目：
        --------
        - Ollama LLM 服务状态
        - 向量数据库连接
        - 文档数量统计
        - 嵌入模型状态
        
        返回值：
        ------
        dict: 健康检查结果字典
            - success: bool, 整体状态
            - ollama_status: str, LLM 服务状态
            - model_name: str, 当前使用的模型
            - document_count: int, 文档数量
            - embedding_model: str, 嵌入模型名称
            - error: str, 错误信息（如果失败）
        """
        try:
            # LLM 服务连接测试
            test_response = self.llm.complete("Hello")
            ollama_status = "正常" if test_response else "异常"
            
            # 向量数据库状态检查
            doc_count = self.get_document_count()
            
            return {
                "success": True,
                "ollama_status": ollama_status,
                "model_name": self.model_name,
                "document_count": doc_count,
                "embedding_model": self.embedding_model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# ================================================================================
# 全局服务管理模块
# ================================================================================

# 全局 RAG 服务实例（单例模式）
rag_service = None

def get_rag_service() -> RAGService:
    """
    RAG 服务实例获取函数
    ===================
    
    功能说明：
    --------
    - 实现单例模式的服务管理
    - 自动加载环境变量配置
    - 提供全局访问入口
    
    配置来源：
    --------
    - 环境变量优先
    - 默认值兜底
    - 支持 .env 文件
    
    环境变量列表：
    -----------
    - OLLAMA_BASE_URL: Ollama 服务地址
    - DEFAULT_MODEL: 默认 LLM 模型名称
    - EMBEDDING_MODEL: 嵌入模型名称
    - DOCUMENTS_PATH: 文档存储路径
    - VECTOR_STORE_PATH: 向量数据库路径
    - CHUNK_SIZE: 文档分块大小
    - CHUNK_OVERLAP: 分块重叠大小
    - TOP_K: 检索返回数量
    
    返回值：
    ------
    RAGService: 配置完成的 RAG 服务实例
    """
    global rag_service
    if rag_service is None:
        # 加载环境变量配置（支持 .env 文件）
        from dotenv import load_dotenv
        load_dotenv()
        
        # 使用环境变量或默认值创建服务实例
        rag_service = RAGService(
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model_name=os.getenv("DEFAULT_MODEL", "maoniang:latest"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            documents_path=os.getenv("DOCUMENTS_PATH", "./documents"),
            vector_store_path=os.getenv("VECTOR_STORE_PATH", "./vector_store"),
            chunk_size=int(os.getenv("CHUNK_SIZE", "1024")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "20")),
            top_k=int(os.getenv("TOP_K", "5"))
        )
    return rag_service
