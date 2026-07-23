# Slide 8 Dataset Distribution Prompt

Create a 16:9 Chinese data-visualization figure titled "训练数据类别分布". Use the concrete dataset-label result image at `presentation/assets/yolo_dataset_labels.jpg` as the data and visual reference. Preserve the visible class-imbalance pattern and bounding-box distribution information, but redraw or re-layout it into a cleaner presentation style suitable for a project defense.

Content:
- Bar chart of 10 lesion categories: 肺不张, 钙化, 实变, 积液, 肺气肿, 纤维化, 骨折, 肿块, 结节, 气胸.
- Highlight low-frequency categories with a subtle warm color.
- Add one concise callout: "少数类别样本不足，模型难以充分学习"
- Optional small inset: bounding-box position distribution heatmap, if it can stay readable.

Style: academic and data-focused, light background, clear axis labels, large Chinese category names, no dense raw training dashboard look. Do not invent precise counts that are not clearly readable from the reference. Use relative bars and explanatory callouts. Add a small caption "基于数据集标签图整理".
