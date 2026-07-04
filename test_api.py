"""
API 调试脚本 - 测试 API 连接 (SDK 版本)
"""
import os
import sys
from pathlib import Path

# 添加 src 到路径
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# 加载 .env 文件
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    print(f"加载配置文件: {env_path}")
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                os.environ[key] = value
                if "key" in key.lower() or "token" in key.lower():
                    print(f"  {key} = {value[:15]}...")
                else:
                    print(f"  {key} = {value}")

print()

# 测试环境变量
api_key = os.getenv("ANTHROPIC_AUTH_TOKEN")
base_url = os.getenv("ANTHROPIC_BASE_URL")

print("=" * 50)
print("  环境变量检查")
print("=" * 50)
print(f"API Key: {'✓ 已设置' if api_key else '✗ 未设置'}")
print(f"Base URL: {'✓ 已设置' if base_url else '✗ 未设置'}")
if base_url:
    print(f"  URL: {base_url}")
print()

# 测试导入
print("=" * 50)
print("  测试官方 SDK API 客户端")
print("=" * 50)
try:
    from api_client import ClaudeAPIClient
    print("✓ API 客户端导入成功")
    client = ClaudeAPIClient()
    print("✓ API 客户端初始化成功")
except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    print()
    input("按 Enter 退出...")
    sys.exit(1)

print()

# 测试 API 调用
print("=" * 50)
print("  测试 API 调用")
print("=" * 50)
try:
    response = client.chat(
        messages=[{"role": "user", "content": "你好，请用一句话介绍自己"}],
        system_prompt="你是一个友好的 AI 助手。",
        max_tokens=100
    )
    print(f"✓ API 调用成功!")
    print(f"响应: {response}")
except Exception as e:
    print(f"✗ API 调用失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 50)
print("  测试完成")
print("=" * 50)
print()
input("按 Enter 退出...")
