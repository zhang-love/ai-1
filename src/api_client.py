"""
Claude API 客户端封装
支持官方 SDK 和火山引擎 HTTP 流式调用
"""
import os
import json
import requests
from typing import List, Dict, Generator, Optional, Union
from anthropic import Anthropic


class ClaudeAPIClient:
    """Claude API 客户端"""

    def __init__(self):
        """初始化 API 客户端，从环境变量读取配置"""
        # 从环境变量读取配置
        self.base_url = os.getenv("ANTHROPIC_BASE_URL", "").rstrip("/")
        self.api_key = os.getenv("ANTHROPIC_AUTH_TOKEN", "")
        self.timeout_ms = int(os.getenv("API_TIMEOUT_MS", "60000"))
        self.timeout = max(10, self.timeout_ms // 1000)  # 至少 10 秒

        # 火山引擎特定配置
        self.volc_access_key = os.getenv("VOLC_ACCESS_KEY", "")
        self.volc_secret_key = os.getenv("VOLC_SECRET_KEY", "")
        self.model_id = os.getenv("MODEL_ID", "claude-opus-4-8-1m")

        # 选择调用模式
        self.use_volc_http = os.getenv("USE_VOLC_HTTP", "true").lower() == "true"

        # 验证配置
        if not self.api_key and not self.volc_access_key:
            raise ValueError("请配置 ANTHROPIC_AUTH_TOKEN 或 VOLC_ACCESS_KEY")

        print(f"  API Base URL: {self.base_url}")
        if self.api_key:
            print(f"  API Key: {self.api_key[:15]}...")
        if self.volc_access_key:
            print(f"  Volc Access Key: {self.volc_access_key[:15]}...")
        print(f"  Model: {self.model_id}")
        print(f"  Timeout: {self.timeout}s")
        print(f"  使用火山引擎 HTTP 模式: {self.use_volc_http}")

        # 初始化官方 SDK 客户端（备用）
        if self.api_key:
            self.client = Anthropic(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )
        else:
            self.client = None

    def _get_volc_url(self) -> str:
        """获取火山引擎 API URL"""
        if self.base_url and "/api/coding" in self.base_url:
            return f"{self.base_url}/v1/chat/completions"
        return "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

    def _get_volc_headers(self) -> Dict[str, str]:
        """获取火山引擎请求头"""
        # 确定使用的 token
        token = self.api_key
        if self.volc_access_key and self.volc_secret_key:
            token = f"{self.volc_access_key}:{self.volc_secret_key}"
        elif self.volc_access_key:
            token = self.volc_access_key

        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

    def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int = 4096
    ) -> str:
        """
        发送对话请求（非流式）

        Args:
            messages: 对话历史，格式为 [{"role": "user"|"assistant", "content": "..."}]
            system_prompt: 系统提示词
            max_tokens: 最大生成 token 数

        Returns:
            AI 回复的文本内容
        """
        if self.use_volc_http:
            return self._chat_volc_http(messages, system_prompt, max_tokens, stream=False)
        elif self.client:
            response = self.client.messages.create(
                model=self.model_id,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages
            )
            return response.content[0].text
        else:
            raise ValueError("没有可用的 API 客户端")

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int = 4096
    ) -> Generator[str, None, None]:
        """
        发送对话请求（流式）

        Args:
            messages: 对话历史
            system_prompt: 系统提示词
            max_tokens: 最大生成 token 数

        Yields:
            AI 回复的文本片段
        """
        if self.use_volc_http:
            yield from self._chat_volc_http_stream(messages, system_prompt, max_tokens)
        elif self.client:
            # 使用官方 SDK 流式
            with self.client.messages.stream(
                model=self.model_id,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    yield text
        else:
            raise ValueError("没有可用的 API 客户端")

    def _chat_volc_http(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int = 4096,
        stream: bool = False
    ) -> Union[str, Generator[str, None, None]]:
        """
        使用火山引擎 HTTP API 调用

        Args:
            messages: 对话历史
            system_prompt: 系统提示词
            max_tokens: 最大生成 token 数
            stream: 是否流式

        Returns:
            完整回复文本或生成器
        """
        url = self._get_volc_url()
        headers = self._get_volc_headers()

        # 构建消息列表，包含系统提示
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        payload = {
            "model": self.model_id,
            "messages": full_messages,
            "stream": stream,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        if stream:
            return self._stream_volc_response(url, headers, payload)
        else:
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

    def _chat_volc_http_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int = 4096
    ) -> Generator[str, None, None]:
        """流式调用火山引擎 HTTP API"""
        return self._chat_volc_http(messages, system_prompt, max_tokens, stream=True)

    def _stream_volc_response(
        self,
        url: str,
        headers: Dict[str, str],
        payload: Dict
    ) -> Generator[str, None, None]:
        """处理流式响应"""
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
