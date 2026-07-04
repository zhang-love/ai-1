"""
客服培训机器人 - 专业版
使用火山引擎 API 流式调用
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
import requests
import json
import os
from pathlib import Path
from typing import Optional, List

app = FastAPI(title="客服培训机器人", version="2.0")

# ===== 配置区域 =====
# 从 .env 文件或环境变量读取
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://ark.cn-beijing.volces.com/api/coding")
ANTHROPIC_AUTH_TOKEN = os.getenv("ANTHROPIC_AUTH_TOKEN", "")
API_TIMEOUT_MS = int(os.getenv("API_TIMEOUT_MS", "60000"))
MODEL_ID = os.getenv("MODEL_ID", "claude-opus-4-8-1m")

# 知识库
knowledge_content = ""
knowledge_file = Path(__file__).parent.parent / "knowledge" / "产品知识库.md"
if knowledge_file.exists():
    with open(knowledge_file, "r", encoding="utf-8") as f:
        knowledge_content = f.read()
        print(f"✅ 知识库加载成功: {knowledge_file.name}")
else:
    print("⚠️ 知识库文件不存在")

# ===== 数据模型 =====
class ChatRequest(BaseModel):
    messages: List[dict]
    stream: Optional[bool] = True
    mode: Optional[str] = "free_chat"


def build_system_prompt(mode: str = "free_chat") -> str:
    """根据模式构建系统提示词"""
    base_prompt = f"""你是一个专业的客服培训助手，帮助新客服学习产品知识和服务技巧。

以下是产品知识库，请基于这些知识回答问题：

{knowledge_content}

## 角色设定
- 友好、专业、耐心
- 回答要基于知识库内容，不要编造信息
- 如果知识库中没有答案，诚实告知
- 用中文回复
- 保持自然对话语气
"""
    return base_prompt


def build_volc_payload(messages: List[dict], stream: bool = True):
    """构建火山引擎API请求体"""
    return {
        "model": MODEL_ID,
        "messages": messages,
        "stream": stream,
        "max_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
    }


def call_volc_stream(payload: dict):
    """流式调用火山引擎API，逐字返回"""
    url = f"{ANTHROPIC_BASE_URL}/v1/messages"

    headers = {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_AUTH_TOKEN,
        "anthropic-version": "2023-06-01"
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            stream=True,
            timeout=API_TIMEOUT_MS // 1000
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    if data_str.strip() == '[DONE]':
                        break
                    try:
                        chunk_data = json.loads(data_str)
                        # 提取 delta 内容
                        if 'content' in chunk_data and len(chunk_data['content']) > 0:
                            content = chunk_data['content'][0].get('text', '')
                            if content:
                                yield f"data: {json.dumps({'text': content}, ensure_ascii=False)}\n\n"
                    except json.JSONDecodeError:
                        continue
    except requests.exceptions.RequestException as e:
        print(f"⚠️ API 请求失败: {e}")
        yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
    finally:
        yield "data: [DONE]\n\n"


# ===== API 路由 =====
@app.get("/", response_class=HTMLResponse)
async def root():
    """主页"""
    index_path = Path(__file__).parent / "templates" / "index_pro.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>客服培训机器人已启动</h1>"


@app.post("/chat")
async def chat(request: ChatRequest):
    """聊天接口 - 流式"""
    if not request.messages:
        raise HTTPException(status_code=400, detail="消息不能为空")

    # 构建请求体：加入系统提示词（作为系统消息放在前面）
    system_prompt = build_system_prompt(request.mode)

    # 消息格式处理
    final_messages = request.messages.copy()

    # 调用API
    payload = {
        "model": MODEL_ID,
        "messages": final_messages,
        "stream": request.stream,
        "max_tokens": 2048,
        "system": system_prompt
    }

    return StreamingResponse(
        call_volc_stream(payload),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/health")
async def health():
    """健康检查"""
    return {
        "status": "ok",
        "model": MODEL_ID,
        "has_knowledge": len(knowledge_content) > 0
    }


@app.get("/api/quick-questions")
async def quick_questions():
    """快捷问题列表"""
    return {
        "questions": [
            {"id": 1, "text": "手柄怎么连接手机？"},
            {"id": 2, "text": "手柄续航时间是多久？"},
            {"id": 3, "text": "如何申请退换货？"},
            {"id": 4, "text": "手柄支持哪些游戏？"}
        ]
    }


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("   🤖 客服培训机器人 v2.0 - 专业版")
    print("=" * 60)
    print(f"   模型: {MODEL_ID}")
    print(f"   API地址: {ANTHROPIC_BASE_URL}")
    print(f"   知识库: {'已加载' if knowledge_content else '未加载'}")
    print()
    print("   🌐 访问地址: http://127.0.0.1:8000")
    print("=" * 60)
    print()

    uvicorn.run(app, host="127.0.0.1", port=8000)
