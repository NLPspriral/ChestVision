"""
文本向量化 — 将文本转换为高维向量

职责：
  - 调用 Embedding API 将文本块转换为向量
  - 支持通义千问 / OpenAI 两种 Embedding 模型
  - 批量处理提升效率

Embedding 模型选择：
  - 通义千问 text-embedding-v3（1024维，推荐）
  - OpenAI text-embedding-3-small（1536维）
"""

from typing import Optional

from app.config.settings import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """文本向量化服务"""

    def __init__(self):
        self._client = None
        self._model = None
        self._init_client()

    def _init_client(self):
        """初始化 Embedding 客户端"""
        try:
            from openai import OpenAI

            qwen_api_key = getattr(settings, "QWEN_API_KEY", "")
            if qwen_api_key and qwen_api_key not in ("", "sk-your-qwen-api-key"):
                self._client = OpenAI(
                    api_key=qwen_api_key,
                    base_url=getattr(
                        settings, "QWEN_BASE_URL",
                        "https://dashscope.aliyuncs.com/compatible-mode/v1",
                    ),
                )
                self._model = getattr(settings, "EMBEDDING_MODEL", "text-embedding-v3")
            else:
                openai_key = getattr(settings, "OPENAI_API_KEY", "")
                if openai_key:
                    self._client = OpenAI(
                        api_key=openai_key,
                        base_url=getattr(
                            settings, "OPENAI_BASE_URL",
                            "https://api.openai.com/v1",
                        ),
                    )
                    self._model = getattr(settings, "EMBEDDING_MODEL", "text-embedding-3-small")

            if self._client:
                logger.info("Embedding服务初始化完成: model=%s", self._model)
            else:
                logger.warning("Embedding服务未配置API Key，向量化功能不可用")
        except Exception as e:
            logger.error("Embedding服务初始化失败: %s", str(e))
            self._client = None

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """批量将文本转换为向量"""
        if not self._client:
            logger.error("Embedding客户端未初始化")
            return [[] for _ in texts]

        try:
            all_embeddings = []
            batch_size = 20

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = self._client.embeddings.create(
                    model=self._model,
                    input=batch,
                )
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

            logger.info("向量化完成: %d条文本, 维度=%d",
                        len(texts), len(all_embeddings[0]) if all_embeddings else 0)
            return all_embeddings
        except Exception as e:
            logger.error("文本向量化失败: %s", str(e))
            return [[] for _ in texts]

    def embed_query(self, query: str) -> Optional[list[float]]:
        """将查询文本转换为向量"""
        results = self.embed_texts([query])
        if results and results[0]:
            return results[0]
        return None

    @property
    def is_available(self) -> bool:
        return self._client is not None


embedding_service = EmbeddingService()
