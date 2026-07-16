"""
云端独立训练脚本

用途：在 AutoDL 等 GPU 云平台上独立运行 YOLO11 训练，不依赖 FastAPI 后端。

示例：
    python tools/train_on_cloud.py --epochs 5 --batch 8
    python tools/train_on_cloud.py --model yolo11s --epochs 100 --batch 16
    python tools/train_on_cloud.py --data datasets/chest_xray/yolo_dataset/data.yaml
"""

import argparse
import os
import sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA_YAML = os.path.join(
    PROJECT_ROOT, "datasets", "chest_xray", "yolo_dataset", "data.yaml"
)
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "runs", "cloud_train")
YOLO11_MODELS = ["yolo11n", "yolo11s", "yolo11m", "yolo11l", "yolo11x"]


def main():
    parser = argparse.ArgumentParser(
        description="YOLO11 云端独立训练脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default="yolo11n",
        choices=YOLO11_MODELS,
        help="基础模型（仅支持 yolo11n/s/m/l/x，默认：yolo11n）",
    )
    parser.add_argument("--epochs", "-e", type=int, default=100, help="训练轮数")
    parser.add_argument("--batch", "-b", type=int, default=16, help="批次大小")
    parser.add_argument("--imgsz", type=int, default=640, help="图像尺寸")
    parser.add_argument("--device", type=str, default="0", help="训练设备")
    parser.add_argument("--optimizer", type=str, default="SGD", help="优化器")
    parser.add_argument("--lr0", type=float, default=0.01, help="初始学习率")
    parser.add_argument("--data", "-d", type=str, default=DEFAULT_DATA_YAML, help="data.yaml 路径")
    parser.add_argument("--output", "-o", type=str, default=DEFAULT_OUTPUT_DIR, help="输出目录")
    parser.add_argument("--name", type=str, default=None, help="实验名称")
    parser.add_argument("--mosaic", type=float, default=1.0, help="Mosaic 增强概率")
    parser.add_argument("--mixup", type=float, default=0.0, help="MixUp 增强概率")
    parser.add_argument("--fliplr", type=float, default=0.5, help="水平翻转概率")
    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"[错误] data.yaml 不存在：{args.data}")
        sys.exit(1)

    if args.name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.name = f"{args.model}_{timestamp}"

    print("=" * 60)
    print("  YOLO11 云端训练")
    print(f"  模型：{args.model}")
    print(f"  数据：{args.data}")
    print(f"  轮数：{args.epochs}")
    print(f"  Batch：{args.batch}")
    print(f"  设备：{args.device}")
    print(f"  优化器：{args.optimizer}")
    print(f"  学习率：{args.lr0}")
    print(f"  输出：{args.output}/{args.name}")
    print("=" * 60)

    from ultralytics import YOLO
    from ultralytics.utils import SETTINGS

    SETTINGS.update(wandb=False)

    model = YOLO(f"{args.model}.pt")
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        optimizer=args.optimizer,
        lr0=args.lr0,
        project=args.output,
        name=args.name,
        exist_ok=True,
        verbose=True,
        save=True,
        plots=True,
        mosaic=args.mosaic,
        mixup=args.mixup,
        fliplr=args.fliplr,
    )

    print("\n" + "=" * 60)
    print("  训练完成！")
    print(f"  输出目录：{os.path.join(args.output, args.name)}")
    print(f"  最优权重：{os.path.join(args.output, args.name, 'weights', 'best.pt')}")
    print(f"  训练日志：{os.path.join(args.output, args.name, 'results.csv')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
