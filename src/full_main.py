"""
Full Version with Claude API Integration
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import uuid
import os
import sys
import json

app = FastAPI()

# Add src to path for imports
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Load .env file from project root
env_path = src_dir.parent / ".env"
if env_path.exists():
    print(f"Loading config from: {env_path}")
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                os.environ[key] = value

template_path = src_dir / "templates" / "index.html"

sessions = {}

# ===== 新增：FAQ 缓存 =====
faq_cache = {}

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

# Global variables for API client and knowledge
api_client = None
knowledge_manager = None
knowledge_content = ""


def initialize_components():
    """Initialize API client and knowledge manager"""
    global api_client, knowledge_manager, knowledge_content

    try:
        # Import our modules
        from api_client import ClaudeAPIClient
        from knowledge import KnowledgeManager

        # Initialize API client - will use environment variables from settings.json
        api_client = ClaudeAPIClient()
        print("✓ API client initialized (SDK mode)")

        # Initialize knowledge manager
        knowledge_manager = KnowledgeManager()
        knowledge_content = knowledge_manager.get_knowledge_content()
        print(f"✓ Knowledge loaded: {knowledge_manager.get_file_list()}")

        # Initialize FAQ cache with predefined responses
        init_faq_cache()

        return True
    except Exception as e:
        print(f"✗ Failed to initialize components: {e}")
        print("  Running in DEMO mode only")
        return False


def init_faq_cache():
    """初始化 FAQ 缓存，预加载常见问题的回复"""
    global faq_cache
    faq_cache = {
        "我的手柄连不上蓝牙怎么办？": "您好！请先检查以下几点：\n1. 确认手柄电量充足\n2. 长按 HOME 键 3 秒进入配对模式\n3. 在手机蓝牙设置中找到并连接 'Flydigi 手柄'",
        "怎么连接蓝牙？": "您好！蓝牙连接步骤如下：\n1. 长按 HOME 键 3 秒开机\n2. 指示灯快闪表示进入配对模式\n3. 在手机蓝牙设置中找到并连接 'Flydigi 手柄'",
        "能退吗？": "您好！我们支持 7 天无理由退换，30 天质量问题包换，1 年质保。请告诉我您的订单号，我会帮您处理的。",
        "可以退换货吗？": "您好！我们支持 7 天无理由退换，30 天质量问题包换，1 年质保。请告诉我您的订单号，我会帮您处理的。",
        "手柄有连发功能吗？": "您好！是的，我们的手柄支持连发功能。您可以通过配套 APP 设置连发速度和按键映射，还有更多高级功能等您探索！",
        "怎么设置连发？": "您好！您可以通过配套 APP 设置连发功能，包括连发速度、按键映射等高级功能。",
        "手柄怎么充电？": "您好！使用 USB-C 数据线连接充电即可，充电时指示灯会亮起，充满后会熄灭。",
        "续航多久？": "您好！不同系列续航时间不同：\n- 八爪鱼系列：约 80 小时\n- 黑武士系列：约 60 小时\n- 黄蜂系列：约 20 小时\n续航时间会受到使用方式和灯效设置的影响。",
    }
    print(f"✓ FAQ cache initialized with {len(faq_cache)} items")


def check_faq_cache(user_msg):
    """检查是否有匹配的 FAQ 缓存"""
    user_msg_lower = user_msg.lower()

    # 精确匹配
    if user_msg in faq_cache:
        return faq_cache[user_msg]

    # 模糊匹配
    for q, a in faq_cache.items():
        if len(q) > 3:  # 避免太短的关键词匹配
            if q[:-1] in user_msg or user_msg in q:
                # 匹配成功，返回答案
                return a

            # 关键词匹配
            keywords = ["蓝牙", "连接", "退换", "连发", "充电", "续航"]
            for kw in keywords:
                if kw in user_msg and kw in q:
                    return a

    return None


api_available = initialize_components()


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
            <title>Customer Service Training Bot</title>
        </head>
        <body>
            <h1>Server is working!</h1>
            <p>Template file missing.</p>
        </body>
        </html>
        """


@app.get("/api/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "api_available": api_available,
        "knowledge_loaded": bool(knowledge_content),
        "faq_cache_size": len(faq_cache)
    }


@app.post("/api/session")
async def create_session():
    """Create new session"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"messages": [], "mode": "free", "scenario": None}
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


@app.post("/api/scenario/{scenario_id}")
async def start_scenario(scenario_id: str, request: Request):
    """Start a training scenario"""
    data = await request.json()
    session_id = data.get("session_id")

    if scenario_id not in SCENARIOS:
        return {"status": "error", "message": "场景不存在"}

    scenario = SCENARIOS[scenario_id]

    if session_id and session_id in sessions:
        sessions[session_id]["mode"] = "scenario"
        sessions[session_id]["scenario"] = scenario_id
        sessions[session_id]["messages"] = []

        # First customer message
        first_msg = scenario["customer"]
        sessions[session_id]["messages"].append({"role": "assistant", "content": first_msg})

        return {
            "status": "ok",
            "scenario": scenario_id,
            "first_message": first_msg
        }

    return {"status": "error", "message": "会话不存在"}


@app.post("/api/chat")
async def chat(request: Request):
    """Chat endpoint with Claude API"""
    try:
        data = await request.json()
        user_msg = data.get("message", "")
        session_id = data.get("session_id")
        mode = data.get("mode", "free")

        # Store message in session
        if session_id and session_id in sessions:
            sessions[session_id]["messages"].append({"role": "user", "content": user_msg})

        reply = None
        is_demo = False
        from_cache = False

        # ===== 优先：检查 FAQ 缓存 =====
        cached_reply = check_faq_cache(user_msg)
        if cached_reply:
            print(f"♻️ Hit FAQ cache for: {user_msg[:20]}...")
            reply = cached_reply
            from_cache = True
        else:
            # Try API FIRST if available
            if api_available and api_client:
                try:
                    from prompts import PromptTemplates

                    # Check if in scenario mode (customer role)
                    if session_id and session_id in sessions:
                        session = sessions[session_id]
                        if session.get("mode") == "scenario":
                            # AI plays customer role
                            system_prompt = PromptTemplates.get_customer_role_prompt(
                                json.dumps(session.get("scenario", ""), ensure_ascii=False),
                                knowledge_content
                            )
                        else:
                            # Normal training mode
                            system_prompt = PromptTemplates.get_system_prompt(knowledge_content)
                    else:
                        system_prompt = PromptTemplates.get_system_prompt(knowledge_content)

                    # Get conversation history
                    messages = []
                    if session_id and session_id in sessions:
                        messages = sessions[session_id]["messages"][-20:]  # Last 20 messages

                    if not messages:
                        messages = [{"role": "user", "content": user_msg}]

                    api_response = api_client.chat(messages, system_prompt)
                    reply = api_response

                except Exception as e:
                    print(f"API Error (falling back to demo mode): {e}")
                    reply = None

            # Fallback to demo mode if API failed or not available
            if reply is None:
                is_demo = True
                responses = {
                    "connect": "您好！请先检查以下几点：\n1. 确认手柄电量充足\n2. 长按 HOME 键 3 秒进入配对模式\n3. 在手机蓝牙设置中找到并连接 'Flydigi 手柄'",
                    "return": "您好！我们支持 7 天无理由退换，30 天质量问题包换，1 年质保。请告诉我您的订单号，我会帮您处理的。",
                    "feature": "您好！是的，我们的手柄支持连发功能。您可以通过配套 APP 设置连发速度和按键映射，还有更多高级功能等您探索！",
                    "default": f"好的，收到您的消息：{user_msg}\n\n这是演示版本的回复，完整版本会基于知识库内容智能回答。"
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

                # Check if in scenario mode - AI plays customer
                if session_id and session_id in sessions:
                    session = sessions[session_id]
                    if session.get("mode") == "scenario":
                        # In scenario mode, AI plays the customer
                        reply = "好的，明白了。还有其他问题吗？"

        # Store response
        if session_id and session_id in sessions:
            sessions[session_id]["messages"].append({"role": "assistant", "content": reply})

        return {"response": reply, "status": "ok", "demo": is_demo, "from_cache": from_cache}

    except Exception as e:
        return {"response": f"错误：{str(e)}", "status": "error"}


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("  Customer Service Training Bot (Full Version)")
    print("=" * 50)
    print(f"Template: {template_path}")
    print(f"Template exists: {template_path.exists()}")
    print(f"API Available: {api_available}")
    print()
    print("Open browser at: http://127.0.0.1:8000")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)
