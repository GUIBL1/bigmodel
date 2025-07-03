"""
RAG Flask API服务
提供REST API接口供前端调用
"""

import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# 设置HuggingFace镜像
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HUGGINGFACE_HUB_CACHE'] = './embeddings_cache'

from rag_core import get_rag_service

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 配置文件上传
UPLOAD_FOLDER = './documents'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc', 'md', 'html', 'xlsx', 'xls', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB最大文件大小

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        rag = get_rag_service()
        health_status = rag.health_check()
        return jsonify(health_status)
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/query', methods=['POST'])
def query_rag():
    """RAG查询接口"""
    try:
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
        
        rag = get_rag_service()
        result = rag.query(question)
        
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
        logger.error(f"RAG查询失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """文档上传接口"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "没有文件"
            }), 400
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "没有选择文件"
            }), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": f"不支持的文件类型。支持的类型: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        logger.info(f"文件已保存: {file_path}")
        
        # 添加文档到RAG系统
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
        logger.error(f"文档上传失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """列出已上传的文档"""
    try:
        documents = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if allowed_file(filename):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_size = os.path.getsize(file_path)
                file_mtime = os.path.getmtime(file_path)
                
                documents.append({
                    "filename": filename,
                    "size": file_size,
                    "modified_time": file_mtime
                })
        
        rag = get_rag_service()
        doc_count = rag.get_document_count()
        
        return jsonify({
            "success": True,
            "documents": documents,
            "total_count": len(documents),
            "indexed_count": doc_count
        })
        
    except Exception as e:
        logger.error(f"列出文档失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/documents/<filename>', methods=['DELETE'])
def delete_document(filename):
    """删除文档"""
    try:
        filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                "success": False,
                "error": "文件不存在"
            }), 404
        
        # 删除文件
        os.remove(file_path)
        logger.info(f"文件已删除: {file_path}")
        
        return jsonify({
            "success": True,
            "message": f"文档 {filename} 删除成功"
        })
        
    except Exception as e:
        logger.error(f"删除文档失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/index/rebuild', methods=['POST'])
def rebuild_index():
    """重建索引"""
    try:
        rag = get_rag_service()
        
        # 清空现有索引
        rag.clear_index()
        
        # 重新添加所有文档
        success = rag.add_documents()
        
        if success:
            doc_count = rag.get_document_count()
            return jsonify({
                "success": True,
                "message": "索引重建成功",
                "document_count": doc_count
            })
        else:
            return jsonify({
                "success": False,
                "error": "索引重建失败"
            }), 500
            
    except Exception as e:
        logger.error(f"重建索引失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/index/clear', methods=['POST'])
def clear_index():
    """清空索引"""
    try:
        rag = get_rag_service()
        
        # 清空现有索引
        success = rag.clear_index()
        
        if success:
            return jsonify({
                "success": True,
                "message": "索引已清空"
            })
        else:
            return jsonify({
                "success": False,
                "error": "索引清空失败"
            }), 500
            
    except Exception as e:
        logger.error(f"清空索引失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/models', methods=['GET'])
def list_models():
    """列出可用的模型"""
    try:
        # 这里可以调用Ollama API获取可用模型列表
        # 暂时返回常用模型
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
        logger.error(f"列出模型失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({
        "success": False,
        "error": "文件过大，最大支持16MB"
    }), 413

@app.errorhandler(404)
def not_found(e):
    """404错误处理"""
    return jsonify({
        "success": False,
        "error": "接口不存在"
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """500错误处理"""
    return jsonify({
        "success": False,
        "error": "内部服务器错误"
    }), 500

if __name__ == '__main__':
    # 初始化RAG服务
    try:
        rag = get_rag_service()
        logger.info("RAG服务初始化成功")
        
        # 启动服务器
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', 5001))
        
        logger.info(f"RAG API服务启动在 http://{host}:{port}")
        app.run(host=host, port=port, debug=True)
        
    except Exception as e:
        logger.error(f"RAG服务启动失败: {e}")
        exit(1)
