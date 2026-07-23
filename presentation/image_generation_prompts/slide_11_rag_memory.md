# Slide 11 RAG And Memory Prompt

Create a 16:9 Chinese technical supplement slide titled "RAG 与记忆机制让回答可追溯". This page should be self-contained and suitable for brief display without detailed narration.

Use a two-part layout:

Left side: RAG workflow
用户问题 → 语义向量化 → 知识库检索 → Top-N 文档片段 → 注入 Prompt → LLM 回复
Include labels: "Embedding", "Pgvector", "相似度阈值", "来源可追溯".

Right side: three-layer memory
- "运行时 State": 单次请求内共享
- "Redis 会话缓存": 近期对话，快速读取
- "PostgreSQL 持久化": 全量消息，历史回溯

At the bottom, show a merged context bar: "身份 + 病例 + 检测历史 + 对话历史". Add one concise conclusion: "回答不只依赖模型记忆，而是结合知识库与上下文".

Style: clean engineering diagram, light background, blue-green and muted purple accents. Avoid too many arrows, raw code, or dense database schema details.
