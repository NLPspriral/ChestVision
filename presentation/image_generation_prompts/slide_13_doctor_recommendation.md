# Slide 13 Doctor Recommendation Prompt

Create a 16:9 Chinese workflow diagram titled "医生推荐与信息接力". The slide should explain how ChestVision recommends suitable doctors while keeping the final relationship controlled by administrator review.

Use a pipeline with four major blocks:
1. "检测任务"
2. "推荐服务"
3. "候选医生列表"
4. "管理员审核"
5. "医患关系建立"

Show recommendation inputs feeding into "推荐服务":
- 本次病灶类型
- 风险等级
- 患者病例
- 患者对话
- 医生自述
- 医生历史病例
- 在管患者数量

The "候选医生列表" block should show example fields, not real names:
"匹配分数", "匹配理由", "适配病灶", "联系方式".

Add a small safety note: "用户选择后进入待确认队列". The visual should communicate that AI assists matching but does not bypass administrative confirmation.

Style: medical workflow plus recommendation-system diagram, light background, blue-green primary accents, orange for review/confirmation. Keep text compact and readable.
