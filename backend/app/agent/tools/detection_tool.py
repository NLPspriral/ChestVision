"""
检测工具集 — Agent 可调用的胸片检测工具

工具列表：
  - detect_single_image: 单张胸片检测
  - detect_batch_images: 批量胸片检测
  - detect_zip_file: ZIP 文件解压后批量检测

设计原则：
  - 每个工具使用 @tool 装饰器定义
  - docstring 必须详细，LLM 通过 docstring 理解工具用途
  - 返回值使用 JSON 字符串（摘要），完整结果存类变量供前端使用
"""

import json
import os

from langchain_core.tools import tool

from app.core.logger import get_logger

logger = get_logger(__name__)

# 工具间共享的检测结果存储（供前端卡片渲染）
_last_result = None


def get_last_result():
    """获取最近一次检测的完整结果"""
    global _last_result
    return _last_result


def clear_last_result():
    """清除缓存的检测结果"""
    global _last_result
    _last_result = None


@tool
def detect_single_image(image_path: str, conf: float = 0.25, iou: float = 0.45) -> str:
    """检测单张胸片图像中的病灶。

    支持10种胸部病变：肺不张(Atelectasis)、钙化(Calcification)、实变(Consolidation)、
    胸腔积液(Effusion)、肺气肿(Emphysema)、纤维化(Fibrosis)、骨折(Fracture)、
    肿块(Mass)、结节(Nodule)、气胸(Pneumothorax)。

    当用户上传了一张胸片并要求检测、识别、分析图中的病灶时使用此工具。

    Args:
        image_path: 胸片图像文件的服务器路径（绝对路径），如 /tmp/chestx_uploads/xxx.png
        conf: 置信度阈值，0~1之间，默认0.25。低于此值的检测结果会被过滤
        iou: NMS（非极大值抑制）IoU阈值，0~1之间，默认0.45

    Returns:
        JSON字符串，包含检测摘要（病灶总数、各类数量、推理耗时）。完整结果存于全局变量供前端渲染。
    """
    from app.services.detection_service import detection_service

    global _last_result

    if not os.path.exists(image_path):
        return json.dumps(
            {"error": "图片文件不存在，请让用户重新上传胸片进行检测。"},
            ensure_ascii=False,
        )

    try:
        result = detection_service.detect_single(image_path, conf=conf, iou=iou)
        _last_result = result
        summary = {
            "total_objects": result.get("total_objects", 0),
            "class_counts": result.get("class_counts", {}),
            "inference_time": result.get("inference_time", 0),
        }
        logger.info("单图检测完成: %s, 病灶数: %d", image_path, summary["total_objects"])
        return json.dumps(summary, ensure_ascii=False)
    except Exception as e:
        logger.error("单图检测失败: %s, 错误: %s", image_path, str(e))
        return json.dumps({"error": f"检测失败: {str(e)}"}, ensure_ascii=False)


@tool
def detect_batch_images(image_paths: list[str], conf: float = 0.25) -> str:
    """批量检测多张胸片图像中的病灶。

    当用户一次上传了多张胸片，或者要求"检测所有胸片"时使用此工具。

    Args:
        image_paths: 胸片图像文件路径列表
        conf: 置信度阈值，默认0.25

    Returns:
        JSON字符串，包含每张胸片的检测结果汇总（图片数、总病灶数、各类别统计、推理耗时）
    """
    from app.services.detection_service import detection_service

    global _last_result

    try:
        result = detection_service.detect_batch(image_paths, conf=conf)
        _last_result = result
        summary = {
            "total_images": result.get("total_images", 0),
            "total_objects": result.get("total_objects", 0),
            "class_counts": result.get("class_counts", {}),
            "total_inference_time": result.get("total_inference_time", 0),
        }
        logger.info("批量检测完成: %d张, 病灶数: %d", len(image_paths), summary["total_objects"])
        return json.dumps(summary, ensure_ascii=False)
    except Exception as e:
        logger.error("批量检测失败: %s", str(e))
        return json.dumps({"error": f"批量检测失败: {str(e)}"}, ensure_ascii=False)


@tool
def detect_zip_file(zip_path: str, conf: float = 0.25) -> str:
    """解压 ZIP 文件并批量检测其中所有胸片图像的病灶。

    当用户上传了ZIP压缩包进行批量检测时使用此工具。

    Args:
        zip_path: ZIP文件的服务器路径
        conf: 置信度阈值，默认0.25

    Returns:
        JSON字符串，包含ZIP内所有胸片的检测结果汇总
    """
    from app.services.detection_service import detection_service

    global _last_result

    try:
        result = detection_service.detect_zip(zip_path, conf=conf)
        _last_result = result
        summary = {
            "total_images": result.get("total_images", 0),
            "total_objects": result.get("total_objects", 0),
            "class_counts": result.get("class_counts", {}),
            "total_inference_time": result.get("total_inference_time", 0),
        }
        logger.info("ZIP检测完成: %s, 病灶数: %d", zip_path, summary["total_objects"])
        return json.dumps(summary, ensure_ascii=False)
    except Exception as e:
        logger.error("ZIP检测失败: %s", str(e))
        return json.dumps({"error": f"ZIP检测失败: {str(e)}"}, ensure_ascii=False)


# 检测工具列表
DETECTION_TOOLS = [
    detect_single_image,
    detect_batch_images,
    detect_zip_file,
]
