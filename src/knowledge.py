"""
知识库管理模块
负责加载和管理 Markdown 格式的产品知识
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
import markdown


class KnowledgeManager:
    """知识库管理器"""

    def __init__(self, knowledge_dir: str = "knowledge"):
        """
        初始化知识库管理器

        Args:
            knowledge_dir: 知识库目录路径
        """
        self.knowledge_dir = Path(knowledge_dir)
        self.knowledge_cache: Dict[str, str] = {}
        self.load_all_knowledge()

    def load_all_knowledge(self):
        """加载目录下所有 Markdown 文件到缓存"""
        if not self.knowledge_dir.exists():
            print(f"警告：知识库目录 {self.knowledge_dir} 不存在")
            return

        # 扫描所有 .md 文件
        for md_file in self.knowledge_dir.glob("*.md"):
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.knowledge_cache[md_file.name] = content
                    print(f"已加载知识库：{md_file.name}")
            except Exception as e:
                print(f"加载 {md_file.name} 失败：{e}")

    def get_knowledge_content(self, filename: Optional[str] = None) -> str:
        """
        获取知识库内容

        Args:
            filename: 指定文件名，不指定则合并所有文件

        Returns:
            知识库文本内容
        """
        if filename and filename in self.knowledge_cache:
            return self.knowledge_cache[filename]
        return "\n\n".join(self.knowledge_cache.values())

    def get_file_list(self) -> List[str]:
        """获取所有知识库文件名列表"""
        return list(self.knowledge_cache.keys())

    def reload_knowledge(self):
        """重新加载所有知识库"""
        self.knowledge_cache.clear()
        self.load_all_knowledge()

    def to_html(self, content: str) -> str:
        """
        将 Markdown 内容转换为 HTML 用于显示

        Args:
            content: Markdown 文本

        Returns:
            HTML 文本
        """
        return markdown.markdown(content)
