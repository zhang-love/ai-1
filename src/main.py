"""
客服培训机器人 - FastAPI 主入口
支持流式响应
"""
import sys
import json
import asyncio
from pathlib import Path
from typing import AsyncGenerator

# 加载 .env 配置
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"[OK] Config loaded: {env_path}")

# 确保可以导入同目录的模块
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

# 导入本地模块
from api_client import ClaudeAPIClient
from knowledge import KnowledgeManager
from chat_manager import ChatManager
from prompts import PromptTemplates

app = FastAPI(title="Customer Service Training Bot")

# 允许 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化管理器
try:
    api_client = ClaudeAPIClient()
    print("[OK] API client initialized")
except Exception as e:
    print(f"[FAIL] API client: {e}")
    api_client = None

# 知识库目录相对于项目根目录
knowledge_dir = src_dir.parent / "knowledge"
knowledge_manager = KnowledgeManager(str(knowledge_dir))

chat_manager = ChatManager()

# 读取 HTML 模板
template_path = src_dir / "templates" / "index.html"
if template_path.exists():
    with open(template_path, 'r', encoding='utf-8') as f:
        HTML_TEMPLATE = f.read()
else:
    HTML_TEMPLATE = "<html><body><h1>Template not found</h1></body></html>"

# 静态文件目录如果不存在就创建
static_dir = src_dir / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    """主页面"""
    return HTMLResponse(content=HTML_TEMPLATE)


@app.post("/api/session")
async def create_session():
    """创建新会话"""
    session = chat_manager.create_session()
    return {"session_id": session.session_id}


@app.post("/api/chat/stream")
async def chat_stream(request: Request):
    """发送消息进行对话（流式）"""
    if not api_client:
        return JSONResponse(
            status_code=500,
            content={"error": "API client not initialized"}
        )

    data = await request.json()
    session_id = data.get("session_id")
    user_message = data.get("message", "")

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")

    session = chat_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")

    # 添加用户消息
    session.add_message("user", user_message)

    # 获取知识库
    knowledge = knowledge_manager.get_knowledge_content()
    system_prompt = PromptTemplates.get_system_prompt(knowledge)

    async def event_generator():
        try:
            full_response = ""
            # 调用流式 API
            for chunk in api_client.chat_stream(
                messages=session.get_history(),
                system_prompt=system_prompt
            ):
                full_response += chunk
                # 以 SSE 格式发送
                yield f"data: {json.dumps({'text': chunk, 'done': False})}\n\n"
                await asyncio.sleep(0)  # 让出控制权

            # 保存完整回复到会话
            session.add_message("assistant", full_response)
            # 发送完成信号
            yield f"data: {json.dumps({'text': '', 'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/knowledge")
async def get_knowledge():
    """获取知识库列表和内容"""
    return {
        "files": knowledge_manager.get_file_list(),
        "content": knowledge_manager.get_knowledge_content()
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "api_client_initialized": api_client is not None,
        "knowledge_files": knowledge_manager.get_file_list()
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting Customer Service Training Bot...")
    print(f"Knowledge files: {knowledge_manager.get_file_list()}")
    print("Open browser at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
