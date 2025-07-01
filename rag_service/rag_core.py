"""
RAG服务核心模块
使用LlamaIndex实现本地RAG功能
"""

import os
import logging
from typing import List, Optional
from pathlib import Path

try:
    # 尝试新版本导入
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
    # 回退到旧版本导入
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
        Settings = None  # 旧版本使用ServiceContext
    except ImportError as e:
        print(f"导入LlamaIndex失败: {e}")
        print("请先运行: pip install llama-index")
        raise

import chromadb
from chromadb.config import Settings as ChromaSettings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    """RAG服务类"""
    
    def __init__(self, 
                 ollama_base_url: str = "http://localhost:11434",
                 model_name: str = "maoniang:latest",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 documents_path: str = "./documents",
                 vector_store_path: str = "./vector_store",
                 chunk_size: int = 1024,
                 chunk_overlap: int = 20,
                 top_k: int = 5):
        
        self.ollama_base_url = ollama_base_url
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.documents_path = Path(documents_path)
        self.vector_store_path = Path(vector_store_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        self.offline_mode = False  # 初始化离线模式标志
        
        # 初始化组件
        self._setup_llm()
        self._setup_embedding()
        self._setup_vector_store()
        self._setup_index()
        
    def _setup_llm(self):
        """设置LLM"""
        try:
            self.llm = Ollama(
                model=self.model_name,
                base_url=self.ollama_base_url,
                request_timeout=60.0
            )
            logger.info(f"LLM设置完成: {self.model_name}")
        except Exception as e:
            logger.error(f"LLM设置失败: {e}")
            raise
    
    def _setup_embedding(self):
        """设置嵌入模型，支持离线模式"""
        # 首先检查网络连接
        def check_internet_connection():
            try:
                import requests
                response = requests.get("https://huggingface.co", timeout=3)
                return response.status_code == 200
            except:
                return False
        
        has_internet = check_internet_connection()
        logger.info(f"网络连接状态: {'可用' if has_internet else '不可用'}")
        
        if has_internet:
            try:
                # 有网络时尝试在线嵌入模型
                logger.info(f"尝试加载在线嵌入模型: {self.embedding_model}")
                self.embed_model = HuggingFaceEmbedding(
                    model_name=self.embedding_model,
                    cache_folder="./embeddings_cache"
                )
                logger.info(f"嵌入模型设置完成: {self.embedding_model}")
                self.offline_mode = False
                return
            except Exception as e:
                logger.warning(f"在线嵌入模型加载失败: {e}")
        
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
                    self.vocab_cache_path = Path("./embeddings_cache/tfidf_vocab.pkl")
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
        """设置向量存储"""
        try:
            # 创建ChromaDB客户端
            chroma_client = chromadb.PersistentClient(
                path=str(self.vector_store_path),
                settings=ChromaSettings(anonymized_telemetry=False)
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
        """设置索引"""
        try:
            # 检查是否为离线模式
            if self.offline_mode:
                logger.info("离线模式：跳过LlamaIndex索引设置")
                self.index = None
                self.query_engine = None
                return
            
            # 根据版本配置
            if Settings is not None:
                # 新版本使用Settings
                Settings.llm = self.llm
                Settings.embed_model = self.embed_model
                if hasattr(Settings, 'node_parser'):
                    Settings.node_parser = SimpleNodeParser.from_defaults(
                        chunk_size=self.chunk_size,
                        chunk_overlap=self.chunk_overlap
                    )
                service_context = None
            else:
                # 旧版本使用ServiceContext
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
        """添加文档到向量存储"""
        try:
            # 检查离线模式
            if self.offline_mode:
                return self._offline_add_documents(file_paths)
            
            if file_paths:
                # 处理指定文件
                documents = []
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        reader = SimpleDirectoryReader(input_files=[file_path])
                        docs = reader.load_data()
                        documents.extend(docs)
                        logger.info(f"加载文档: {file_path}")
            else:
                # 处理文档目录中的所有文件
                if not self.documents_path.exists():
                    self.documents_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"创建文档目录: {self.documents_path}")
                    return True
                
                reader = SimpleDirectoryReader(
                    input_dir=str(self.documents_path),
                    recursive=True
                )
                documents = reader.load_data()
            
            if not documents:
                logger.warning("没有找到文档")
                return True
            
            # 添加文档到索引
            for doc in documents:
                self.index.insert(doc)
            
            logger.info(f"成功添加 {len(documents)} 个文档到索引")
            return True
            
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return False
    
    def query(self, question: str) -> dict:
        """查询RAG系统"""
        try:
            if not question.strip():
                return {
                    "success": False,
                    "error": "问题不能为空"
                }
            
            logger.info(f"查询问题: {question}")
            
            # 检查是否为离线模式
            if self.offline_mode:
                return self._offline_query(question)
            
            # 在线模式：使用LlamaIndex查询
            response = self.query_engine.query(question)
            
            # 提取源文档信息
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
        """离线查询方法"""
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
        """离线模式下添加文档"""
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
        """简单的文本提取"""
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
        """简单的文本分块"""
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
        """获取文档数量"""
        try:
            # 通过向量存储获取文档数量
            collection = self.vector_store._collection
            return collection.count()
        except Exception as e:
            logger.error(f"获取文档数量失败: {e}")
            return 0
    
    def clear_index(self) -> bool:
        """清空索引"""
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
        """健康检查"""
        try:
            # 检查Ollama连接
            test_response = self.llm.complete("Hello")
            ollama_status = "正常" if test_response else "异常"
            
            # 检查向量存储
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

# 全局RAG服务实例
rag_service = None

def get_rag_service() -> RAGService:
    """获取RAG服务实例"""
    global rag_service
    if rag_service is None:
        # 从环境变量加载配置
        from dotenv import load_dotenv
        load_dotenv()
        
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
