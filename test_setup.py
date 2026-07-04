#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试环境设置"""
import sys
import os
from pathlib import Path

# 添加 src 目录到路径
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# 加载 .env
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print("[OK] Config loaded")

# 测试 API 客户端
from api_client import ClaudeAPIClient
try:
    client = ClaudeAPIClient()
    print("[OK] API client initialized")
    print(f"     Model: {client.model_id}")
except Exception as e:
    print(f"[FAIL] API client: {e}")
    sys.exit(1)

# 测试知识库
from knowledge import KnowledgeManager
try:
    km = KnowledgeManager(str(Path(__file__).parent / "knowledge"))
    print(f"[OK] Knowledge base: {km.get_file_list()}")
except Exception as e:
    print(f"[FAIL] Knowledge base: {e}")
    sys.exit(1)

print("\nAll tests passed! Ready to start server.")
