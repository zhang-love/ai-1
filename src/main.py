"""
客服培训机器人 - FastAPI 主入口
支持流式响应
"""
import sys
import json
from pathlib import Path
from typing import AsyncGenerator

# 加载 .env 配置
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ 已加载配置文件: {env_path}")

# 确保可以导入同目录的模块
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

# 导入本地模块
from api_client import ClaudeAPIClient
from knowledge import KnowledgeManager
from chat_manager import ChatManager
from prompts import PromptTemplates

app = FastAPI(title="客服培训机器人", description="基于 Claude API 的客服培训系统")

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
    print("API 客户端初始化成功")
except Exception as e:
    print(f"API 客户端初始化失败：{e}")
    api_client = None

# 知识库目录相对于项目根目录
knowledge_dir = src_dir.parent / "knowledge"
knowledge_manager = KnowledgeManager(str(knowledge_dir))

chat_manager = ChatManager()

# 模板和静态文件
templates = Jinja2Templates(directory=str(src_dir / "templates"))

# 静态文件目录如果不存在就创建
static_dir = src_dir / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 预设场景
SCENARIOS = {
    "connection": {
        "name": "产品连接问题",
        "description": "客户遇到蓝牙连接问题",
        "customer_prompt": """你是一个不太懂技术的客户，刚买了游戏手柄但连不上蓝牙。
对话流程：
1. 你先说："你好，我的手柄连不上蓝牙怎么办？"
2. 等待客服回复
3. 如果客服给了步骤，你说："我试了，还是连不上，还有其他方法吗？"
4. 继续对话"""
    },
    "return": {
        "name": "退换货咨询",
        "description": "客户想了解退换货政策",
        "customer_prompt": """你是一个比较着急的客户，想了解退换货。
对话流程：
1. 你先说："你好，我买的手柄能退吗？"
2. 等待客服回复
3. 然后问："那怎么操作呢？"
4. 继续对话"""
    },
    "feature": {
        "name": "功能咨询",
        "description": "客户想了解产品功能",
        "customer_prompt": """你是一个想了解手柄功能的客户。
对话流程：
1. 你先说："你好，这个手柄有连发功能吗？"
2. 等待客服回复
3. 然后问："那怎么设置呢？"
4. 继续对话"""
    }
}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """主页面"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/session")
async def create_session():
    """创建新会话"""
    session = chat_manager.create_session()
    return {"session_id": session.session_id}


@app.post("/api/chat")
async def chat(request: Request):
    """
    发送消息进行对话（非流式）

    请求体格式：
    {
        "session_id": "会话ID",
        "message": "用户消息",
        "mode": "free_chat|role_play|scenario",
        "scenario_id": "场景ID（场景模式时需要）"
    }
    """
    if not api_client:
        return JSONResponse(
            status_code=500,
            content={"error": "API 客户端未初始化，请检查配置"}
        )

    data = await request.json()
    session_id = data.get("session_id")
    user_message = data.get("message", "")
    mode = data.get("mode", "free_chat")
    scenario_id = data.get("scenario_id")

    if not session_id:
        raise HTTPException(status_code=400, detail="缺少 session_id")

    session = chat_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 添加用户消息
    session.add_message("user", user_message)
    session.mode = mode

    # 获取知识库
    knowledge = knowledge_manager.get_knowledge_content()

    try:
        if mode == "role_play" and scenario_id and scenario_id in SCENARIOS:
            # 角色扮演模式：AI 扮演客户
            scenario = SCENARIOS[scenario_id]
            system_prompt = PromptTemplates.get_customer_role_prompt(
                scenario["customer_prompt"],
                knowledge
            )
        else:
            # 自由问答模式：AI 扮演培训助手
            system_prompt = PromptTemplates.get_system_prompt(knowledge)

        # 调用 API
        response = api_client.chat(
            messages=session.get_history(),
            system_prompt=system_prompt
        )
        session.add_message("assistant", response)
        return {"response": response, "session_id": session_id}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


async def generate_stream(
    session,
    system_prompt: str,
    session_id: str
) -> AsyncGenerator[str, None]:
    """生成流式响应"""
    try:
        full_response = ""
        # 调用流式 API
        for chunk in api_client.chat_stream(
            messages=session.get_history(),
            system_prompt=system_prompt
        ):
            full_response += chunk
            # 以 SSE 格式发送
            yield f"data: {json.dumps({'text': chunk, 'done': False}, ensure_ascii=False)}\n\n"

        # 保存完整回复到会话
        session.add_message("assistant", full_response)
        # 发送完成信号
        yield f"data: {json.dumps({'text': '', 'done': True, 'session_id': session_id}, ensure_ascii=False)}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e), 'done': True}, ensure_ascii=False)}\n\n"


@app.post("/api/chat/stream")
async def chat_stream(request: Request):
    """
    发送消息进行对话（流式）

    请求体格式：
    {
        "session_id": "会话ID",
        "message": "用户消息",
        "mode": "free_chat|role_play|scenario",
        "scenario_id": "场景ID（场景模式时需要）"
    }
    """
    if not api_client:
        return JSONResponse(
            status_code=500,
            content={"error": "API 客户端未初始化，请检查配置"}
        )

    data = await request.json()
    session_id = data.get("session_id")
    user_message = data.get("message", "")
    mode = data.get("mode", "free_chat")
    scenario_id = data.get("scenario_id")

    if not session_id:
        raise HTTPException(status_code=400, detail="缺少 session_id")

    session = chat_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 添加用户消息
    session.add_message("user", user_message)
    session.mode = mode

    # 获取知识库
    knowledge = knowledge_manager.get_knowledge_content()

    # 构建系统提示词
    if mode == "role_play" and scenario_id and scenario_id in SCENARIOS:
        scenario = SCENARIOS[scenario_id]
        system_prompt = PromptTemplates.get_customer_role_prompt(
            scenario["customer_prompt"],
            knowledge
        )
    else:
        system_prompt = PromptTemplates.get_system_prompt(knowledge)

    # 返回流式响应
    return StreamingResponse(
        generate_stream(session, system_prompt, session_id),
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


@app.get("/api/scenarios")
async def get_scenarios():
    """获取预设场景列表"""
    return {
        "scenarios": [
            {"id": k, "name": v["name"], "description": v["description"]}
            for k, v in SCENARIOS.items()
        ]
    }


@app.post("/api/knowledge/reload")
async def reload_knowledge():
    """重新加载知识库"""
    knowledge_manager.reload_knowledge()
    return {"message": "知识库已重新加载", "files": knowledge_manager.get_file_list()}


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
    print("🚀 启动客服培训机器人...")
    print(f"📚 知识库目录：{knowledge_dir}")
    print(f"📄 知识库文件：{knowledge_manager.get_file_list()}")
    print("🌐 访问地址：http://localhost:8000")
    print("✨ 支持流式响应")
    uvicorn.run(app, host="0.0.0.0", port=8000)
