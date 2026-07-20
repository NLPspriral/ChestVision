"""
对话记忆管理 — 基于 Redis 的对话历史存储（补充 DB 持久化）

职责：
  - 保存用户对话消息到 Redis（支持 TTL 过期）
  - 加载历史消息作为 Agent 上下文（快速缓存层）
  - 管理会话（创建、获取、删除）

注意：
  - 本模块是 DB 持久化（chat_service）的补充缓存层
  - 主要用途是为 Agent 提供快速的对话历史上下文
  - Redis 不可用时自动降级到内存缓存

Redis key 设计：
  chat:session:{user_id}:{session_id}  → [msg1_json, msg2_json, ...]  TTL=3600s
  chat:sessions:{user_id}              → [session_id1, session_id2, ...]
"""

import json
import time

from app.core.logger import get_logger
from app.storage.redis_client import redis_client

logger = get_logger(__name__)

# 配置常量
MAX_HISTORY_MESSAGES = 20  # 最多加载的历史消息数
SESSION_TTL = 3600  # 会话过期时间（秒），1小时


class ConversationMemory:
    """对话记忆管理器（Redis缓存层）"""

    def __init__(self, max_messages: int = MAX_HISTORY_MESSAGES, ttl: int = SESSION_TTL):
        self.max_messages = max_messages
        self.ttl = ttl
        self.redis = redis_client

    def _session_key(self, user_id: int, session_id: str) -> str:
        return f"chat:session:{user_id}:{session_id}"

    def _index_key(self, user_id: int) -> str:
        return f"chat:sessions:{user_id}"

    def save_message(self, user_id: int, session_id: str, role: str, content: str):
        """保存一条对话消息到 Redis 缓存"""
        key = self._session_key(user_id, session_id)
        message = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
        }

        try:
            self.redis.lpush(key, json.dumps(message, ensure_ascii=False))
            self.redis.expire(key, self.ttl)

            # 更新会话索引
            exists_key = f"chat:exists:{user_id}:{session_id}"
            if not self.redis.exists(exists_key):
                self.redis.lpush(self._index_key(user_id), session_id)
                self.redis.set(exists_key, "1", expire=86400)

            logger.debug("缓存消息: user=%d, session=%s, role=%s", user_id, session_id, role)
        except Exception as e:
            logger.warning("Redis消息缓存失败: %s", str(e))

    def load_history(self, user_id: int, session_id: str) -> list[dict]:
        """从 Redis 加载会话历史消息"""
        key = self._session_key(user_id, session_id)

        try:
            raw_messages = self.redis.lrange(key, 0, -1)
            if not raw_messages:
                return []

            messages = []
            for raw in raw_messages[-self.max_messages:]:
                try:
                    msg = json.loads(raw) if isinstance(raw, str) else raw
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", ""),
                    })
                except (json.JSONDecodeError, AttributeError):
                    continue

            logger.debug("加载缓存历史: user=%d, session=%s, 消息数=%d",
                         user_id, session_id, len(messages))
            return messages
        except Exception as e:
            logger.debug("Redis历史加载失败: %s", str(e))
            return []

    def get_sessions(self, user_id: int) -> list[str]:
        """获取用户的会话 ID 列表"""
        try:
            index_key = self._index_key(user_id)
            sessions = self.redis.lrange(index_key, 0, -1)
            return sessions if sessions else []
        except Exception:
            return []

    def clear_session(self, user_id: int, session_id: str):
        """清空指定会话的缓存"""
        try:
            key = self._session_key(user_id, session_id)
            self.redis.delete(key)
            logger.info("清空会话缓存: user=%d, session=%s", user_id, session_id)
        except Exception as e:
            logger.warning("清空会话缓存失败: %s", str(e))


# 全局单例
conversation_memory = ConversationMemory()
