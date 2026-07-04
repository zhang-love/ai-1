"""
对话管理模块
负责管理会话、历史记录等
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class Message:
    """单条消息"""
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: Optional[str] = None


class ChatSession:
    """单个对话会话"""

    def __init__(self, session_id: Optional[str] = None):
        """
        初始化会话

        Args:
            session_id: 会话 ID，不指定则自动生成
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.now().isoformat()
        self.messages: List[Message] = []
        self.mode = "free_chat"  # free_chat | role_play | scenario

    def add_message(self, role: str, content: str):
        """
        添加消息到会话

        Args:
            role: 角色 (user | assistant | system)
            content: 消息内容
        """
        self.messages.append(Message(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat()
        ))

    def get_history(self, limit: int = 20) -> List[Dict[str, str]]:
        """
        获取对话历史

        Args:
            limit: 限制返回的消息条数，避免上下文过长

        Returns:
            消息列表，格式为 [{"role": "...", "content": "..."}]
        """
        # 取最近的 limit 条消息
        messages = self.messages[-limit:]
        return [{"role": m.role, "content": m.content} for m in messages]

    def to_dict(self) -> Dict:
        """将会话转换为字典格式"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "messages": [
                {"role": m.role, "content": m.content, "timestamp": m.timestamp}
                for m in self.messages
            ],
            "mode": self.mode
        }


class ChatManager:
    """会话管理器，管理多个会话"""

    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}

    def create_session(self) -> ChatSession:
        """
        创建新会话

        Returns:
            新会话对象
        """
        session = ChatSession()
        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        获取会话

        Args:
            session_id: 会话 ID

        Returns:
            会话对象，不存在则返回 None
        """
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """
        删除会话

        Args:
            session_id: 会话 ID

        Returns:
            是否删除成功
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
