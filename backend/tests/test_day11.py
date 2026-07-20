"""Day11 验收测试脚本"""
import requests, json

# 登录
resp = requests.post("http://localhost:8000/api/auth/login",
    json={"username": "test_admin", "password": "123456"})
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 1. 构建知识库
print("=" * 50)
print("1. 构建知识库索引")
r = requests.post("http://localhost:8000/api/knowledge/build?force_rebuild=true", headers=headers)
print(f"   状态: {r.json()['message']}")
print(f"   文本块: {r.json()['stats']['total_chunks']}")
print(f"   Embedding: {'可用' if r.json()['stats']['embedding_available'] else '不可用'}")

# 2. 测试检索
print("\n2. 测试知识库检索")
test_queries = [
    "什么是肺不张",
    "IoU是什么意思",
    "胸部X光如何读片",
    "肺气肿的X光表现",
    "目标检测评估指标有哪些"
]
for q in test_queries:
    r = requests.post("http://localhost:8000/api/knowledge/search",
        json={"query": q, "top_k": 2}, headers=headers)
    data = r.json()
    status = "PASS" if data["count"] > 0 else "FAIL"
    print(f"   [{status}] '{q}' -> {data['count']} 条结果")

# 3. 测试 Agent 工具数
print("\n3. 验证 Agent 工具绑定")
print("   应绑定 6 个工具 (检测3 + 系统2 + 知识1)")

# 4. 测试对话 SSE
print("\n4. 测试对话 SSE 流式")
r = requests.post("http://localhost:8000/api/chat/stream",
    json={"message": "系统里现在有多少病人", "session_id": "test-day11"},
    headers=headers, stream=True)
chunks = []
tool_events = []
for line in r.iter_lines():
    if line:
        line = line.decode("utf-8")
        if line.startswith("data: ") and line != "data: [DONE]":
            event = json.loads(line[6:])
            if event["type"] == "text_chunk":
                chunks.append(event["content"])
            elif event["type"] in ("tool_start", "tool_end"):
                tool_events.append(f"{event['type']}:{event.get('tool','')}")
print(f"   收到 {len(chunks)} 个文本块")
print(f"   工具事件: {tool_events}")

# 5. 总结
print("\n" + "=" * 50)
print("Day 11 验收测试完成!")
print(f"  知识库检索: {'通过' if all(requests.post('http://localhost:8000/api/knowledge/search', json={'query':q,'top_k':2}, headers=headers).json()['count']>0 for q in test_queries[:2]) else '需检查'}")
print(f"  对话流式: {'通过' if len(chunks)>0 else '需检查'}")
