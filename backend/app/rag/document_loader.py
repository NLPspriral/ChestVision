"""
文档加载与分块 — 将知识文档切分为可检索的文本块

职责：
  - 读取 Markdown/TXT 格式的知识文档
  - 智能分块（按段落 + 标题层级）
  - 保留文档元数据（文件名、标题等）

分块策略：
  - chunk_size=500：每块约500个字符
  - chunk_overlap=50：相邻块有50字符重叠，避免语义被截断
"""

import os
from pathlib import Path

from app.core.logger import get_logger

logger = get_logger(__name__)

# 知识库文档目录
KNOWLEDGE_BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "knowledge_base",
)


class DocumentLoader:
    """文档加载器"""

    @staticmethod
    def load_documents(base_dir: str = None) -> list[dict]:
        """加载知识库中的所有文档"""
        if base_dir is None:
            base_dir = KNOWLEDGE_BASE_DIR

        documents = []
        base_path = Path(base_dir)

        if not base_path.exists():
            logger.warning("知识库目录不存在: %s", base_dir)
            return documents

        for file_path in sorted(base_path.glob("*.md")) + sorted(base_path.glob("*.txt")):
            try:
                content = file_path.read_text(encoding="utf-8")
                title = DocumentLoader._extract_title(content, file_path.stem)

                documents.append({
                    "content": content,
                    "metadata": {
                        "source": file_path.name,
                        "title": title,
                        "file_path": str(file_path),
                    },
                })
                logger.info("加载文档: %s (%d字符)", file_path.name, len(content))
            except Exception as e:
                logger.error("加载文档失败: %s, 错误: %s", file_path, str(e))

        logger.info("共加载 %d 个文档", len(documents))
        return documents

    @staticmethod
    def split_documents(
        documents: list[dict],
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> list[dict]:
        """将文档切分为文本块"""
        chunks = []

        for doc in documents:
            content = doc["content"]
            metadata = doc["metadata"]
            paragraphs = content.split("\n\n")
            current_chunk = ""
            current_headers = []

            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                # 追踪标题层级
                if para.startswith("#"):
                    current_headers = [
                        h for h in current_headers
                        if h["level"] < len(para) - len(para.lstrip("#"))
                    ]
                    current_headers.append({
                        "level": len(para) - len(para.lstrip("#")),
                        "text": para.lstrip("#").strip(),
                    })

                # 判断是否切分
                if len(current_chunk) + len(para) + 2 > chunk_size and current_chunk:
                    header_context = " > ".join(h["text"] for h in current_headers)
                    chunks.append({
                        "content": current_chunk.strip(),
                        "metadata": {
                            **metadata,
                            "header_context": header_context,
                            "chunk_index": len(chunks),
                        },
                    })
                    if chunk_overlap > 0 and len(current_chunk) > chunk_overlap:
                        current_chunk = current_chunk[-chunk_overlap:] + "\n\n" + para
                    else:
                        current_chunk = para
                else:
                    current_chunk = current_chunk + "\n\n" + para if current_chunk else para

            # 保存最后一块
            if current_chunk.strip():
                header_context = " > ".join(h["text"] for h in current_headers)
                chunks.append({
                    "content": current_chunk.strip(),
                    "metadata": {
                        **metadata,
                        "header_context": header_context,
                        "chunk_index": len(chunks),
                    },
                })

        logger.info("文档分块完成: %d个文档 → %d个文本块", len(documents), len(chunks))
        return chunks

    @staticmethod
    def _extract_title(content: str, default: str) -> str:
        """从 Markdown 内容中提取一级标题"""
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("# ") and not line.startswith("## "):
                return line[2:].strip()
        return default


document_loader = DocumentLoader()
