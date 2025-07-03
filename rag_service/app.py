"""
AI智能对话系统 - RAG Flask API服务

功能概述：
本模块是RAG（检索增强生成）系统的核心API服务，基于Flask框架构建，
为前端提供完整的文档处理、向量检索和智能问答功能。

核心功能模块：
1. 文档管理：文档上传、列表查看、删除操作
2. RAG查询：基于本地知识库的智能问答
3. 索引管理：向量索引的重建、清空操作
4. 系统监控：健康检查、模型列表等

技术栈：
- Flask: Web框架和API服务
- LlamaIndex: RAG框架和向量检索
- ChromaDB: 向量数据库存储
- Ollama: 本地大语言模型推理
- HuggingFace: 文本嵌入模型

API接口设计：
- RESTful风格的HTTP接口
- JSON格式的请求和响应
- 统一的错误处理机制
- CORS跨域支持

部署说明：
- 默认端口：5001
- 支持的文件格式：txt, pdf, docx, md, html, xlsx, csv等
- 最大文件大小：16MB
- 文档存储路径：./documents
- 向量存储路径：./vector_store

创建时间：2025年7月3日
版本：v1.0.0
许可证：MIT License
"""

# ========================= 系统依赖导入 =========================
import os                                    # 操作系统接口模块
import logging                               # 日志记录模块
from flask import Flask, request, jsonify, send_from_directory  # Flask Web框架
from flask_cors import CORS                  # Flask跨域资源共享
from werkzeug.utils import secure_filename   # 安全文件名处理
from dotenv import load_dotenv              # 环境变量加载

# ========================= 环境配置 =========================
"""
HuggingFace环境配置
设置镜像源和缓存路径，解决国内网络访问问题
"""
# 设置HuggingFace镜像源（使用国内镜像加速下载）
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
# 设置HuggingFace模型缓存目录
os.environ['HUGGINGFACE_HUB_CACHE'] = './embeddings_cache'

# ========================= RAG核心模块导入 =========================
from rag_core import get_rag_service        # 导入RAG服务核心模块

# ========================= 配置初始化 =========================
# 加载.env文件中的环境变量配置
load_dotenv()

# 配置日志系统：设置日志级别为INFO，便于调试和监控
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================= Flask应用初始化 =========================
"""
Flask应用和中间件配置
"""
# 创建Flask应用实例
app = Flask(__name__)
# 启用CORS跨域支持，允许前端从不同域名访问API
CORS(app)

# ========================= 文件上传配置 =========================
"""
文档上传相关配置
定义支持的文件类型、存储路径、大小限制等
"""
UPLOAD_FOLDER = './documents'               # 文档存储目录
ALLOWED_EXTENSIONS = {                      # 支持的文件扩展名集合
    'txt',    # 纯文本文件
    'pdf',    # PDF文档  
    'docx',   # Word文档（新格式）
    'doc',    # Word文档（旧格式）
    'md',     # Markdown文档
    'html',   # HTML网页文件
    'xlsx',   # Excel表格（新格式）
    'xls',    # Excel表格（旧格式）
    'csv'     # CSV数据文件
}

# Flask应用配置
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 文件大小限制：16MB

# 确保文档存储目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ========================= 工具函数定义 =========================
def allowed_file(filename):
    """
    检查上传文件的类型是否在允许列表中
    
    参数：
        filename (str): 待检查的文件名
        
    返回：
        bool: True表示文件类型被允许，False表示不被允许
        
    逻辑：
        1. 检查文件名是否包含点号
        2. 提取文件扩展名并转为小写
        3. 判断扩展名是否在允许的集合中
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ========================= 系统监控API =========================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    系统健康检查接口
    
    功能：检查RAG系统各组件的运行状态
    方法：GET
    路径：/api/health
    
    返回内容：
        - ollama_status: Ollama服务状态
        - model_name: 当前使用的模型名称
        - document_count: 已索引的文档数量
        - embedding_model: 嵌入模型名称
        - mode: 运行模式（online/offline）
    
    响应格式：
        成功: {"success": True, "ollama_status": "正常", ...}
        失败: {"success": False, "error": "错误信息"}
    """
    try:
        # 获取RAG服务实例并执行健康检查
        rag = get_rag_service()
        health_status = rag.health_check()
        return jsonify(health_status)
    except Exception as e:
        # 记录错误日志并返回错误响应
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ========================= RAG查询API =========================

@app.route('/api/query', methods=['POST'])
def query_rag():
    """
    RAG智能问答接口（本地知识库查询）
    
    功能：基于本地知识库进行智能问答
    方法：POST
    路径：/api/query
    
    请求体参数：
        question (str): 用户问题，必填参数
    
    请求示例：
        {
            "question": "什么是人工智能？"
        }
    
    业务流程：
        1. 参数验证：检查问题是否为空
        2. RAG查询：在本地知识库中检索相关文档
        3. 智能回答：基于检索结果生成答案
        4. 自动修复：检测并自动修复索引问题
        5. 返回结果：包含答案、来源文档等信息
    
    自动修复机制：
        - 检测向量维度不匹配问题
        - 检测文档索引缺失问题
        - 自动重建索引并重新查询
    
    响应格式：
        成功: {
            "success": True,
            "answer": "智能生成的答案",
            "sources": [{"file_name": "文档名", "score": 0.95}],
            "question": "原始问题",
            "rebuilt_index": True/False  // 是否重建了索引
        }
        失败: {"success": False, "error": "错误信息"}
    """
    try:
        # ========== 请求参数验证阶段 ==========
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({
                "success": False,
                "error": "缺少问题参数"
            }), 400
        
        question = data['question'].strip()
        if not question:
            return jsonify({
                "success": False,
                "error": "问题不能为空"
            }), 400
        
        logger.info(f"收到RAG查询: {question}")
        
        # ========== RAG查询执行阶段 ==========
        rag = get_rag_service()
        result = rag.query(question)
        
        # ========== 自动修复检测阶段 ==========
        # 检查是否需要重建索引
        needs_rebuild = False
        rebuild_reason = ""
        
        if not result.get("success"):
            error_msg = result.get("error", "").lower()
            
            # 检查是否是向量维度不匹配错误
            if result.get("dimension_mismatch"):
                needs_rebuild = True
                rebuild_reason = "向量维度不匹配"
            # 检查是否是"没有找到相关文档"错误
            elif "没有找到相关文档" in error_msg or "没有找到文档索引" in error_msg:
                # 检查是否有文档文件但索引为空
                doc_count = rag.get_document_count()
                if doc_count == 0:
                    # 检查documents目录是否有文件
                    import os
                    documents_path = rag.documents_path
                    if os.path.exists(documents_path):
                        file_count = sum(1 for f in os.listdir(documents_path) 
                                       if os.path.isfile(os.path.join(documents_path, f)))
                        if file_count > 0:
                            needs_rebuild = True
                            rebuild_reason = f"发现{file_count}个文档文件但索引为空"
        
        # ========== 自动修复执行阶段 ==========
        # 执行自动重建
        if needs_rebuild:
            logger.info(f"检测到需要重建索引: {rebuild_reason}")
            logger.info("尝试自动重建索引...")
            
            if rag.clear_index():
                # 重新添加所有文档
                if rag.add_documents():
                    # 重新查询
                    logger.info("索引重建完成，重新执行查询...")
                    result = rag.query(question)
                    if result.get("success"):
                        result["rebuilt_index"] = True
                        result["rebuild_reason"] = rebuild_reason
                        logger.info("索引重建成功，查询已完成")
                    else:
                        logger.error("索引重建后查询仍然失败")
                        result["rebuild_attempted"] = True
                        result["rebuild_reason"] = rebuild_reason
                else:
                    logger.error("重新添加文档失败")
                    result["rebuild_failed"] = "添加文档失败"
            else:
                logger.error("索引重建失败")
                result["rebuild_failed"] = "清空索引失败"
        
        return jsonify(result)
        
    except Exception as e:
        # 异常处理：记录详细错误信息
        logger.error(f"RAG查询失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ========================= 文档管理API =========================

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """
    文档上传接口
    
    功能：上传文档文件并自动建立向量索引
    方法：POST
    路径：/api/upload
    内容类型：multipart/form-data
    
    请求参数：
        file: 文件对象，支持多种格式
    
    支持的文件格式：
        - 文本文件：txt, md, html
        - 办公文档：pdf, docx, doc
        - 数据文件：xlsx, xls, csv
    
    业务流程：
        1. 文件验证：检查文件存在性和格式
        2. 安全处理：使用secure_filename确保文件名安全
        3. 文件保存：存储到指定目录
        4. 索引建立：自动将文档加入RAG系统
        5. 返回结果：包含文件名和处理状态
    
    文件大小限制：16MB
    安全措施：文件名过滤、类型检查
    
    响应格式：
        成功: {
            "success": True,
            "message": "文档 filename.txt 上传并索引成功",
            "filename": "filename.txt"
        }
        失败: {"success": False, "error": "错误描述"}
    """
    try:
        # ========== 文件存在性检查 ==========
        # 检查请求中是否包含文件
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "没有文件"
            }), 400
        
        file = request.files['file']
        
        # ========== 文件名验证 ==========
        # 检查是否选择了文件
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "没有选择文件"
            }), 400
        
        # ========== 文件类型验证 ==========
        # 检查文件扩展名是否在允许列表中
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": f"不支持的文件类型。支持的类型: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
        
        # ========== 文件保存阶段 ==========
        # 使用secure_filename确保文件名安全
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        logger.info(f"文件已保存: {file_path}")
        
        # ========== 文档索引阶段 ==========
        # 将上传的文档添加到RAG系统中
        rag = get_rag_service()
        success = rag.add_documents([file_path])
        
        if success:
            return jsonify({
                "success": True,
                "message": f"文档 {filename} 上传并索引成功",
                "filename": filename
            })
        else:
            return jsonify({
                "success": False,
                "error": "文档索引失败"
            }), 500
            
    except Exception as e:
        # 异常处理：记录错误并返回详细信息
        logger.error(f"文档上传失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """
    文档列表查询接口
    
    功能：获取所有已上传文档的详细信息
    方法：GET
    路径：/api/documents
    
    返回信息：
        - documents: 文档列表，包含每个文档的详细信息
        - total_count: 文件系统中的文档总数
        - indexed_count: 已建立索引的文档数量
    
    每个文档的信息结构：
        - filename: 文件名
        - size: 文件大小（字节）
        - modified_time: 最后修改时间（时间戳）
    
    用途：
        - 前端文档管理界面展示
        - 监控文档索引状态
        - 文档统计分析
    
    响应格式：
        成功: {
            "success": True,
            "documents": [
                {
                    "filename": "example.txt",
                    "size": 1024,
                    "modified_time": 1672531200
                }
            ],
            "total_count": 5,
            "indexed_count": 5
        }
        失败: {"success": False, "error": "错误信息"}
    """
    try:
        # ========== 文档信息收集阶段 ==========
        documents = []
        # 遍历上传目录中的所有文件
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            # 只处理允许的文件类型
            if allowed_file(filename):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_size = os.path.getsize(file_path)      # 获取文件大小
                file_mtime = os.path.getmtime(file_path)    # 获取修改时间
                
                documents.append({
                    "filename": filename,
                    "size": file_size,
                    "modified_time": file_mtime
                })
        
        # ========== 索引状态检查阶段 ==========
        # 获取已索引的文档数量
        rag = get_rag_service()
        doc_count = rag.get_document_count()
        
        return jsonify({
            "success": True,
            "documents": documents,
            "total_count": len(documents),     # 文件系统中的文档数
            "indexed_count": doc_count         # 已索引的文档数
        })
        
    except Exception as e:
        # 异常处理
        logger.error(f"列出文档失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/documents/<filename>', methods=['DELETE'])
def delete_document(filename):
    """
    文档删除接口
    
    功能：删除指定的文档文件
    方法：DELETE
    路径：/api/documents/<filename>
    
    路径参数：
        filename: 要删除的文件名
    
    安全措施：
        - 使用secure_filename处理文件名，防止路径遍历攻击
        - 检查文件存在性，避免删除不存在的文件
        - 只能删除上传目录中的文件
    
    注意事项：
        - 此接口只删除文件系统中的文件
        - 不会自动从向量索引中移除对应的文档块
        - 如需完全清理，建议删除后重建索引
    
    业务流程：
        1. 文件名安全处理
        2. 检查文件存在性
        3. 执行文件删除
        4. 记录操作日志
        5. 返回删除结果
    
    响应格式：
        成功: {
            "success": True,
            "message": "文档 filename.txt 删除成功"
        }
        文件不存在: {"success": False, "error": "文件不存在"} (404)
        失败: {"success": False, "error": "错误信息"} (500)
    """
    try:
        # ========== 文件名安全处理 ==========
        # 使用secure_filename防止路径遍历攻击
        filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # ========== 文件存在性检查 ==========
        if not os.path.exists(file_path):
            return jsonify({
                "success": False,
                "error": "文件不存在"
            }), 404
        
        # ========== 文件删除操作 ==========
        os.remove(file_path)
        logger.info(f"文件已删除: {file_path}")
        
        return jsonify({
            "success": True,
            "message": f"文档 {filename} 删除成功"
        })
        
    except Exception as e:
        # 异常处理：记录错误并返回详细信息
        logger.error(f"删除文档失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ========================= 索引管理API =========================

@app.route('/api/index/rebuild', methods=['POST'])
def rebuild_index():
    """
    索引重建接口
    
    功能：清空现有索引并重新构建所有文档的向量索引
    方法：POST
    路径：/api/index/rebuild
    
    使用场景：
        - 嵌入模型更换后需要重新计算向量
        - 索引损坏或向量维度不匹配
        - 文档内容更新后需要刷新索引
        - 系统升级后的索引兼容性问题
    
    操作流程：
        1. 清空现有的向量索引
        2. 扫描documents目录中的所有文档
        3. 重新提取文本内容并分块
        4. 计算文档向量嵌入
        5. 重新建立向量索引
        6. 返回重建结果统计
    
    注意事项：
        - 重建过程可能需要较长时间，取决于文档数量
        - 重建期间RAG查询功能不可用
        - 建议在系统空闲时执行
    
    响应格式：
        成功: {
            "success": True,
            "message": "索引重建成功",
            "document_count": 15
        }
        失败: {"success": False, "error": "索引重建失败"}
    """
    try:
        # 获取RAG服务实例
        rag = get_rag_service()
        
        # ========== 索引清空阶段 ==========
        logger.info("开始清空现有索引...")
        rag.clear_index()
        
        # ========== 索引重建阶段 ==========
        logger.info("开始重新添加所有文档...")
        success = rag.add_documents()
        
        if success:
            # 获取重建后的文档数量
            doc_count = rag.get_document_count()
            logger.info(f"索引重建成功，共处理 {doc_count} 个文档")
            return jsonify({
                "success": True,
                "message": "索引重建成功",
                "document_count": doc_count
            })
        else:
            logger.error("索引重建失败")
            return jsonify({
                "success": False,
                "error": "索引重建失败"
            }), 500
            
    except Exception as e:
        # 异常处理
        logger.error(f"重建索引失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/index/clear', methods=['POST'])
def clear_index():
    """
    索引清空接口
    
    功能：清空所有向量索引数据
    方法：POST
    路径：/api/index/clear
    
    使用场景：
        - 重新开始构建知识库
        - 清理测试数据
        - 解决索引损坏问题
        - 系统维护需要
    
    操作影响：
        - 清空ChromaDB中的所有向量数据
        - 清空文档元数据和索引信息
        - 不会删除原始文档文件
        - 清空后需要重新上传或重建索引
    
    安全提醒：
        - 此操作不可逆，请谨慎使用
        - 建议在操作前备份重要数据
        - 清空后RAG查询将无法正常工作
    
    响应格式：
        成功: {
            "success": True,
            "message": "索引已清空"
        }
        失败: {"success": False, "error": "索引清空失败"}
    """
    try:
        # 获取RAG服务实例
        rag = get_rag_service()
        
        # ========== 索引清空操作 ==========
        logger.info("开始清空向量索引...")
        success = rag.clear_index()
        
        if success:
            logger.info("向量索引已成功清空")
            return jsonify({
                "success": True,
                "message": "索引已清空"
            })
        else:
            logger.error("索引清空操作失败")
            return jsonify({
                "success": False,
                "error": "索引清空失败"
            }), 500
            
    except Exception as e:
        # 异常处理
        logger.error(f"清空索引失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ========================= 模型管理API =========================

@app.route('/api/models', methods=['GET'])
def list_models():
    """
    可用模型列表接口
    
    功能：获取系统中可用的大语言模型列表
    方法：GET
    路径：/api/models
    
    返回信息：
        - 模型名称：用于Ollama调用的模型标识
        - 模型描述：模型的简要说明
        - 适用场景：推荐的使用场景
    
    扩展计划：
        - 后续可集成Ollama API获取实际可用模型
        - 添加模型状态检查（是否已下载）
        - 支持模型切换功能
        - 添加模型性能参数信息
    
    响应格式：
        成功: {
            "success": True,
            "models": [
                {
                    "name": "llama3.1",
                    "description": "Llama 3.1 模型"
                }
            ]
        }
        失败: {"success": False, "error": "错误信息"}
    """
    try:
        # ========== 模型信息定义 ==========
        # TODO: 后续可以调用Ollama API获取实际可用模型列表
        # 当前返回常用的开源模型列表
        models = [
            {"name": "llama3.1", "description": "Llama 3.1 模型"},
            {"name": "qwen2", "description": "Qwen2 模型"},
            {"name": "chatglm3", "description": "ChatGLM3 模型"},
            {"name": "mistral", "description": "Mistral 模型"}
        ]
        
        return jsonify({
            "success": True,
            "models": models
        })
        
    except Exception as e:
        # 异常处理
        logger.error(f"列出模型失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
# ========================= 错误处理器 =========================
@app.errorhandler(413)
def too_large(e):
    """
    文件过大错误处理器
    
    功能：处理上传文件超过大小限制的情况
    错误码：413 Request Entity Too Large
    触发条件：上传文件大小超过16MB
    
    返回格式：
        {
            "success": False,
            "error": "文件过大，最大支持16MB"
        }
    """
    return jsonify({
        "success": False,
        "error": "文件过大，最大支持16MB"
    }), 413

@app.errorhandler(404)
def not_found(e):
    """
    404错误处理器
    
    功能：处理API接口不存在的情况
    错误码：404 Not Found
    触发条件：访问不存在的API路径
    
    返回格式：
        {
            "success": False,
            "error": "接口不存在"
        }
    """
    return jsonify({
        "success": False,
        "error": "接口不存在"
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """
    500错误处理器
    
    功能：处理服务器内部错误
    错误码：500 Internal Server Error
    触发条件：服务器内部异常未被捕获
    
    返回格式：
        {
            "success": False,
            "error": "内部服务器错误"
        }
    """
    return jsonify({
        "success": False,
        "error": "内部服务器错误"
    }), 500

# ========================= 服务器启动配置 =========================

if __name__ == '__main__':
    """
    RAG API服务器启动入口
    
    启动流程：
        1. 初始化RAG服务组件
        2. 检查系统依赖和配置
        3. 启动Flask Web服务器
        4. 开始监听API请求
    
    配置说明：
        - 主机地址：从环境变量FLASK_HOST获取，默认0.0.0.0（允许外部访问）
        - 监听端口：从环境变量FLASK_PORT获取，默认5001
        - 调试模式：开启调试模式，便于开发和问题排查
        - 自动重载：代码修改后自动重启服务
    
    环境变量：
        - FLASK_HOST: 服务器绑定的主机地址
        - FLASK_PORT: 服务器监听端口
        - 其他RAG相关配置见rag_core.py
    
    部署建议：
        - 生产环境建议关闭debug模式
        - 使用WSGI服务器（如Gunicorn）部署
        - 配置反向代理（如Nginx）
        - 设置适当的安全策略
    """
    # ========== RAG服务初始化 ==========
    try:
        logger.info("开始初始化RAG服务组件...")
        rag = get_rag_service()
        logger.info("RAG服务初始化成功")
        
        # ========== 服务器配置 ==========
        # 从环境变量获取服务器配置，提供默认值
        host = os.getenv('FLASK_HOST', '0.0.0.0')    # 默认允许外部访问
        port = int(os.getenv('FLASK_PORT', 5001))    # 默认端口5001
        
        # ========== 启动信息输出 ==========
        logger.info("=====================================")
        logger.info("   RAG API服务器启动中...          ")
        logger.info("=====================================")
        logger.info(f"服务地址: http://{host}:{port}")
        logger.info(f"监听端口: {port}")
        logger.info(f"主机地址: {host}")
        logger.info(f"文档目录: {UPLOAD_FOLDER}")
        logger.info(f"支持格式: {', '.join(ALLOWED_EXTENSIONS)}")
        logger.info("=====================================")
        
        # ========== Flask服务器启动 ==========
        logger.info(f"RAG API服务启动在 http://{host}:{port}")
        app.run(host=host, port=port, debug=True)
        
    except Exception as e:
        # ========== 启动失败处理 ==========
        logger.error("===================================")
        logger.error("   RAG服务启动失败！             ")
        logger.error("===================================")
        logger.error(f"错误详情: {e}")
        logger.error("请检查以下项目:")
        logger.error("1. Ollama服务是否启动")
        logger.error("2. 模型是否已下载")
        logger.error("3. 端口是否被占用")
        logger.error("4. 依赖包是否完整安装")
        logger.error("===================================")
        exit(1)  # 退出程序
