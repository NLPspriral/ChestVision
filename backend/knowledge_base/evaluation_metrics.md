# 目标检测评估指标

## IoU（Intersection over Union，交并比）

IoU 是衡量两个边界框重叠程度的指标：

IoU = 交集面积 / 并集面积

- IoU = 1：两个框完全重合（最佳检测）
- IoU = 0：两个框完全不重叠
- IoU > 0.5：通常认为检测结果正确
- IoU > 0.75：检测精度较高

在目标检测中的用途：
1. **评估指标**：判断预测框与真实标注框的匹配程度
2. **NMS（非极大值抑制）**：去除重叠度高的重复检测框

## Precision（精确率）与 Recall（召回率）

### Precision（精确率）
Precision = TP / (TP + FP)
含义：在所有被检测出的病灶中，有多少是正确的

### Recall（召回率）
Recall = TP / (TP + FN)
含义：在所有真实病灶中，有多少被成功检测到

在胸片检测中：
- 高Precision → 误诊少，检测结果可信度高
- 高Recall → 漏诊少，覆盖面广

## mAP（mean Average Precision）

mAP是目标检测最常用的综合评估指标。

- mAP50：IoU阈值为0.5时的mAP
- mAP50-95：IoU从0.5到0.95（步长0.05）的平均mAP，更严格

## 混淆矩阵（Confusion Matrix）

|            | 预测阳性 | 预测阴性 |
|------------|---------|---------|
| 实际阳性    | TP      | FN      |
| 实际阴性    | FP      | TN      |

- **TP（True Positive）**：正确检测到的病灶
- **FP（False Positive）**：误检（将正常组织识别为病灶）
- **FN（False Negative）**：漏检（未检测到的真实病灶）
- **TN（True Negative）**：正确排除的正常区域

## F1-Score

F1 = 2 × (Precision × Recall) / (Precision + Recall)

F1是Precision和Recall的调和平均数，综合衡量模型性能。在医疗影像检测中，通常追求较高的F1分数以确保诊断的可靠性。
