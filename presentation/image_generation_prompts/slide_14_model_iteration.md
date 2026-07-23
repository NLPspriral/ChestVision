# Slide 14 Model Iteration Loop Prompt

Create a 16:9 Chinese closed-loop process diagram titled "训练、登记、切换形成模型迭代闭环". The image should explain how ChestVision updates its detection model over time.

Use a loop or left-to-right pipeline with feedback:
数据集上传 → 远程训练 → 产物校验 → 模型版本登记 → 默认模型切换 → 推理服务更新

Key technical labels to include:
- "OSS 分片上传": large dataset upload
- "PAI-DLC 云上容器训练": remote training
- "best.pt / results.csv": training artifacts
- "model_versions": version registry
- "本地推理缓存": inference cache

Show that the Web backend only handles orchestration and status sync, not heavy training. Add a small note: "后端编排，训练上云". Use a clean engineering-process style with concise Chinese labels. Avoid making this look like a cloud vendor advertisement; keep it neutral and project-focused.
