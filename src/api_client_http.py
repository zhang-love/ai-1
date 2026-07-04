"""
Claude API 客户端封装（火山引擎豆包兼容格式）
使用 OpenAI 兼容格式：/api/v3/chat/completions
"""
import os
import json
import requests
from typing import List, Dict


class ClaudeAPIClient:
    """Claude API 客户端"""

    def __init__(self):
        """初始化 API 客户端，从环境变量读取配置"""
        # 从环境变量读取配置
        self.base_url = os.getenv("ANTHROPIC_BASE_URL", "").rstrip("/")
        self.api_key = os.getenv("ANTHROPIC_AUTH_TOKEN", "")
        self.timeout = int(os.getenv("API_TIMEOUT_MS", "300000"))

        # 验证配置
        if not self.api_key:
            raise ValueError("ANTHROPIC_AUTH_TOKEN 未设置，请检查环境变量")

        print(f"  API Base URL: {self.base_url}")
        print(f"  API Key: {self.api_key[:15]}...")

        # 使用的模型 - 火山引擎需要从控制台获取
        self.model = os.getenv("MODEL_ID", "claude-opus-4-8-1m")

    def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int = 4096
    ) -> str:
        """
        发送对话请求

        Args:
            messages: 对话历史，格式为 [{"role": "user"|"assistant", "content": "..."}]
            system_prompt: 系统提示词
            max_tokens: 最大生成 token 数

        Returns:
            AI 回复的文本内容
        """
        try:
            # 构建完整 URL - 正确处理 base_url
            # 如果 base_url 以 /api/coding 结尾，替换为正确的路径
            url = self.base_url
            if "/api/coding" in url:
                # 移除 /api/coding 并添加正确的 /api/v3/chat/completions
                url = url.replace("/api/coding", "") + "/api/v3/chat/completions"
            elif url.endswith("/api"):
                # 如果以 /api 结尾
                url = url + "/v3/chat/completions"
            elif not url.endswith("/api/v3/chat/completions"):
                # 默认情况，添加正确路径
                url = url.rstrip("/") + "/api/v3/chat/completions"

            # 构建请求体 - OpenAI 兼容格式
            full_messages = []
            if system_prompt:
                full_messages.append({"role": "system", "content": system_prompt})
            full_messages.extend(messages)

            payload = {
                "model": self.model,
                "messages": full_messages,
                "max_tokens": max_tokens
            }

            # 发送请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            print(f"  Sending request to: {url}")
            print(f"  Model: {self.model}")

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout // 1000  # convert to seconds
            )

            response.raise_for_status()
            result = response.json()

            # 提取响应 - OpenAI 兼容格式
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            elif "content" in result and len(result["content"]) > 0:
                return result["content"][0]["text"]
            else:
                return f"无法解析响应: {json.dumps(result, ensure_ascii=False)}"

        except Exception as e:
            print(f"  API Error: {e}")
            raise Exception(f"API 调用失败: {str(e)}")
