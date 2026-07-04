"""
Claude API 客户端封装
支持火山引擎 HTTP 流式调用
"""
import os
import json
import requests
from typing import List, Dict, Generator


class ClaudeAPIClient:
    """Claude API 客户端"""

    def __init__(self):
        """初始化 API 客户端，从环境变量读取配置"""
        # 从环境变量读取配置
        self.base_url = os.getenv("ANTHROPIC_BASE_URL", "")
        self.api_key = os.getenv("ANTHROPIC_AUTH_TOKEN", "")
        self.timeout_ms = int(os.getenv("API_TIMEOUT_MS", "60000"))
        self.timeout = max(10, self.timeout_ms // 1000)
        self.model_id = os.getenv("MODEL_ID", "claude-opus-4-8-1m")

        # 验证配置
        if not self.api_key:
            raise ValueError("ANTHROPIC_AUTH_TOKEN not set")

        print(f"  API Base URL: {self.base_url}")
        print(f"  API Key: {self.api_key[:15]}...")
        print(f"  Model: {self.model_id}")
        print(f"  Timeout: {self.timeout}s")

    def _get_url(self) -> str:
        """获取 API URL"""
        if self.base_url:
            if self.base_url.endswith("/v3/chat/completions"):
                return self.base_url
            if "/api/coding" in self.base_url:
                return self.base_url.rstrip("/") + "/v3/chat/completions"
            return self.base_url.rstrip("/") + "/v3/chat/completions"
        return "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int = 4096
    ) -> str:
        """
        发送对话请求（非流式）
        """
        url = self._get_url()
        headers = self._get_headers()

        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        payload = {
            "model": self.model_id,
            "messages": full_messages,
            "stream": False,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int = 4096
    ) -> Generator[str, None, None]:
        """
        发送对话请求（流式）
        """
        url = self._get_url()
        headers = self._get_headers()

        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        payload = {
            "model": self.model_id,
            "messages": full_messages,
            "stream": True,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            stream=True,
            timeout=self.timeout
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
                        delta = chunk_data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
