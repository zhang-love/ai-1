"""
测试脚本 - 验证 Python 环境
"""
import sys
import os

print("=" * 50)
print("   客服培训机器人 - 环境测试")
print("=" * 50)
print()

print(f"[1] Python 版本: {sys.version}")
print(f"[2] Python 路径: {sys.executable}")
print()

print("[3] 检查依赖...")
try:
    import fastapi
    print("    ✓ fastapi 已安装")
except ImportError:
    print("    ✗ fastapi 未安装")

try:
    import uvicorn
    print("    ✓ uvicorn 已安装")
except ImportError:
    print("    ✗ uvicorn 未安装")

try:
    import anthropic
    print("    ✓ anthropic 已安装")
except ImportError:
    print("    ✗ anthropic 未安装")
print()

print("[4] 检查项目文件...")
src_dir = os.path.join(os.path.dirname(__file__), "src")
print(f"    源代码目录: {src_dir}")
if os.path.exists(src_dir):
    print("    ✓ 源代码目录存在")
    files = os.listdir(src_dir)
    for f in sorted(files):
        print(f"      - {f}")
else:
    print("    ✗ 源代码目录不存在")

knowledge_dir = os.path.join(os.path.dirname(__file__), "knowledge")
print(f"    知识库目录: {knowledge_dir}")
if os.path.exists(knowledge_dir):
    print("    ✓ 知识库目录存在")
    files = os.listdir(knowledge_dir)
    for f in sorted(files):
        print(f"      - {f}")
else:
    print("    ✗ 知识库目录不存在")
print()

print("[5] 检查环境变量...")
env_vars = ["ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "API_TIMEOUT_MS"]
for var in env_vars:
    value = os.environ.get(var, "")
    if value:
        if "TOKEN" in var or "KEY" in var:
            display = value[:10] + "..."
        else:
            display = value
        print(f"    ✓ {var} = {display}")
    else:
        print(f"    - {var} = (未设置)")
print()

print("=" * 50)
print("   测试完成！")
print("=" * 50)
print()
input("按 Enter 键退出...")
