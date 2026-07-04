"""
Simple Server with All APIs
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import uuid
import json

app = FastAPI()

src_dir = Path(__file__).parent
template_path = src_dir / "templates" / "index.html"

sessions = {}

# Sample scenarios
SCENARIOS = {
    "connect": {
        "name": "连接问题",
        "description": "客户咨询手柄蓝牙连接问题",
        "customer": "我的手柄连不上蓝牙怎么办？"
    },
    "return": {
        "name": "退换货",
        "description": "客户想申请退换货",
        "customer": "我买的手柄能退吗？"
    },
    "feature": {
        "name": "功能咨询",
        "description": "客户想了解产品功能",
        "customer": "这个手柄有连发功能吗？"
    }
}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page"""
    if template_path.exists():
        html_content = template_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    else:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Customer Service Training Bot</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; height: 100vh; }
                .sidebar { width: 260px; background: #1a1a2e; color: white; padding: 20px; display: flex; flex-direction: column; }
                .chat-area { flex: 1; display: flex; flex-direction: column; background: #f0f2f5; }
                .header { padding: 20px; background: white; border-bottom: 1px solid #e0e0e0; }
                .messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
                .message { max-width: 70%; padding: 12px 16px; border-radius: 12px; line-height: 1.5; }
                .user { background: #0084ff; color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
                .assistant { background: white; color: #333; align-self: flex-start; border-bottom-left-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
                .input-area { padding: 20px; background: white; border-top: 1px solid #e0e0e0; display: flex; gap: 12px; }
                .input-area input { flex: 1; padding: 12px 16px; border: 1px solid #e0e0e0; border-radius: 24px; font-size: 15px; outline: none; }
                .input-area input:focus { border-color: #0084ff; }
                .input-area button { padding: 12px 24px; background: #0084ff; color: white; border: none; border-radius: 24px; font-size: 15px; cursor: pointer; }
                .input-area button:hover { background: #0066cc; }
                .sidebar h2 { margin-bottom: 20px; font-size: 18px; }
                .sidebar-btn { padding: 14px 16px; background: #16213e; border: none; color: white; text-align: left; border-radius: 8px; cursor: pointer; margin-bottom: 8px; font-size: 14px; }
                .sidebar-btn:hover { background: #0f3460; }
            </style>
        </head>
        <body>
            <div class="sidebar">
                <h2>🤖 客服培训</h2>
                <button class="sidebar-btn" onclick="switchMode('free')">💬 自由问答</button>
                <button class="sidebar-btn" onclick="switchMode('scenario')">🎯 场景模拟</button>
                <button class="sidebar-btn" onclick="switchMode('roleplay')">🎭 角色扮演</button>
            </div>
            <div class="chat-area">
                <div class="header">
                    <h3>客服培训助手</h3>
                </div>
                <div class="messages" id="messages">
                    <div class="message assistant">你好！我是客服培训助手，有什么可以帮你的吗？</div>
                </div>
                <div class="input-area">
                    <input type="text" id="userInput" placeholder="输入消息..." onkeypress="if(event.key==='Enter')sendMessage()">
                    <button onclick="sendMessage()">发送</button>
                </div>
            </div>
            <script>
                async function sendMessage() {
                    const input = document.getElementById('userInput');
                    const message = input.value.trim();
                    if (!message) return;

                    const messagesDiv = document.getElementById('messages');
                    const userDiv = document.createElement('div');
                    userDiv.className = 'message user';
                    userDiv.textContent = message;
                    messagesDiv.appendChild(userDiv);
                    input.value = '';
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;

                    const typingDiv = document.createElement('div');
                    typingDiv.className = 'message assistant';
                    typingDiv.textContent = '正在输入...';
                    messagesDiv.appendChild(typingDiv);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;

                    await new Promise(r => setTimeout(r, 1000));

                    messagesDiv.removeChild(typingDiv);
                    const aiDiv = document.createElement('div');
                    aiDiv.className = 'message assistant';
                    aiDiv.textContent = '这是一个演示回复。完整版本需要连接 API。';
                    messagesDiv.appendChild(aiDiv);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }

                function switchMode(mode) {
                    alert('切换到 ' + mode + ' 模式（演示版）');
                }
            </script>
        </body>
        </html>
        """


@app.get("/api/health")
async def health():
    """Health check"""
    return {"status": "ok"}


@app.post("/api/session")
async def create_session():
    """Create new session"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"messages": [], "mode": "free"}
    return {"session_id": session_id}


@app.get("/api/scenarios")
async def get_scenarios():
    """Get scenarios"""
    return {
        "scenarios": [
            {"id": k, "name": v["name"], "description": v["description"]}
            for k, v in SCENARIOS.items()
        ]
    }


@app.post("/api/chat")
async def chat(request: Request):
    """Simple chat endpoint"""
    try:
        data = await request.json()
        user_msg = data.get("message", "")
        mode = data.get("mode", "free")

        responses = {
            "connect": "您好！请先检查以下几点：\n1. 确认手柄电量充足\n2. 长按 HOME 键 3 秒进入配对模式\n3. 在手机蓝牙设置中找到并连接 'Flydigi 手柄'",
            "return": "您好！我们支持 7 天无理由退换，30 天质量问题包换，1 年质保。请告诉我您的订单号，我会帮您处理的。",
            "feature": "您好！是的，我们的手柄支持连发功能。您可以通过配套 APP 设置连发速度和按键映射，还有更多高级功能等您探索！",
            "default": f"好的，收到您的消息：{user_msg}\n\n这是演示版本的回复，配置 API 后会基于知识库内容智能回答。"
        }

        reply = responses.get("default")
        if mode in responses:
            reply = responses[mode]
        elif "蓝牙" in user_msg or "连接" in user_msg:
            reply = responses["connect"]
        elif "退" in user_msg or "换" in user_msg:
            reply = responses["return"]
        elif "功能" in user_msg or "连发" in user_msg:
            reply = responses["feature"]

        return {"response": reply, "status": "ok"}
    except Exception as e:
        return {"response": f"错误：{str(e)}", "status": "error"}


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("  Customer Service Training Bot (Simple Version)")
    print("=" * 50)
    print(f"Template: {template_path}")
    print(f"Template exists: {template_path.exists()}")
    print()
    print("Open browser at: http://127.0.0.1:8000")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)
