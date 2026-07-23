# Slide 9 History-Aware Analysis Prompt

Create a 16:9 Chinese process diagram titled "检测结果如何进入病史感知分析". The slide should explain that ChestVision does not stop at drawing lesion boxes; it persists results and combines them with patient context for analysis.

Use a left-to-right pipeline:
1. "胸片上传"
2. "YOLO 检测"
3. "结果入库"
4. "拉取病史"
5. "LLM 综合分析"

Under each step, add short labels:
- 胸片上传: 单图 / 批量 / ZIP
- YOLO 检测: 类别 / 置信度 / 边界框 / 标注图
- 结果入库: detection_tasks / detection_results
- 拉取病史: 患者档案 / 最近病例 / 历史检测
- LLM 综合分析: 病灶解释 / 风险提示 / 复查建议 / 报告草稿

Show a side panel titled "输出价值" with three items: "不是孤立看图", "结合历史变化", "便于医生接力". Use clean medical-tech process styling, concise Chinese labels, and subtle arrows. Avoid making the slide look like a software stack diagram; it should focus on the clinical information flow.
