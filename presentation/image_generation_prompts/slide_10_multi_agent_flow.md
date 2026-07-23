# Slide 10 Multi-Agent Flow Prompt

Create a 16:9 Chinese process diagram titled "先判断问题，再交给对应能力处理". It should explain ChestVision's multi-agent conversation workflow in a simple way for a non-expert audience.

Main flow:
用户输入 → Supervisor 路由 → 专业节点 → Supervisor 统一回复

Show the Supervisor routing block with two internal mechanisms:
- "规则快速路由": 附件、检测、报告、治疗等明确关键词
- "LLM 语义兜底": 复杂表达、上下文追问

Professional nodes:
- Detection: 胸片检测
- Diagnosis: 诊断分析
- Report: 报告生成
- Case Plan: 病例分析
- QA: 医学问答

Show that Detection can automatically continue to Diagnosis. Show that all nodes return to Supervisor before the final response. Use Chinese labels only on the diagram. Keep the diagram visually lighter and simpler than a software architecture diagram; it should be easy to explain in one minute.

Style: consistent with the deck, light background, blue-green main flow, purple for AI nodes, orange only for fallback/attention. Avoid excessive arrows, long paragraphs, or internal implementation terms that are not needed on stage.
