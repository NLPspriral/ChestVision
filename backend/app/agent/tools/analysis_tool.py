"""
系统查询工具 — Agent 可调用的数据查询工具

工具列表：
  - query_system_info: 查询系统信息（患者、医生、检测统计、病灶分布等）
  - generate_report: 为检测任务生成结构化诊断报告
"""

import json

from langchain_core.tools import tool

from app.core.logger import get_logger

logger = get_logger(__name__)

# 当前请求用户引用（由 Agent 设置）
_current_user = None


def set_current_user(user):
    """设置当前请求用户"""
    global _current_user
    _current_user = user


@tool
def query_system_info(query_type: str) -> str:
    """查询系统信息，自动根据当前用户权限过滤。

    支持的查询类型：
    - patients: 患者总数（适合问"有几个病人"）
    - my_patients: 患者完整列表，含编号/姓名/年龄/性别（适合问"有哪些病人""病人列表"）
    - doctors: 医生总数
    - users: 用户分类统计（仅管理员）
    - detections: 检测任务总数
    - my_records: 我的病例列表（适合问"我的病例"）
    - records: 病例总数
    - recent: 最近7天检测统计
    - lesions: 病灶分布统计

    Args:
        query_type: 查询类型，必须是上述值之一

    Returns:
        JSON字符串，包含对应的查询结果
    """
    from app.database.session import SessionLocal
    from app.entity.db_models import (
        DetectionTask,
        DoctorPatientRelation,
        MedicalRecord,
        PatientProfile,
        User,
    )

    global _current_user
    user = _current_user
    db = SessionLocal()
    try:
        if query_type == "patients":
            if user and user.user_type == "admin":
                count = db.query(PatientProfile).count()
            elif user and user.user_type == "doctor":
                count = (
                    db.query(DoctorPatientRelation)
                    .filter(
                        DoctorPatientRelation.doctor_id == user.id,
                        DoctorPatientRelation.relation_status == "active",
                    )
                    .count()
                )
            else:
                count = 1 if user else 0
            return json.dumps({"patients": count}, ensure_ascii=False)
        elif query_type == "doctors":
            count = db.query(User).filter(User.user_type == "doctor").count()
            return json.dumps({"doctors": count}, ensure_ascii=False)
        elif query_type == "users":
            total = db.query(User).count()
            patients = db.query(User).filter(User.user_type == "patient").count()
            doctors = db.query(User).filter(User.user_type == "doctor").count()
            admins = db.query(User).filter(User.user_type == "admin").count()
            return json.dumps(
                {
                    "total_users": total,
                    "patients": patients,
                    "doctors": doctors,
                    "admins": admins,
                },
                ensure_ascii=False,
            )
        elif query_type == "detections":
            count = db.query(DetectionTask).count()
            completed = (
                db.query(DetectionTask)
                .filter(DetectionTask.status == "completed")
                .count()
            )
            return json.dumps(
                {"total_detections": count, "completed": completed},
                ensure_ascii=False,
            )
        elif query_type == "records":
            count = db.query(MedicalRecord).count()
            return json.dumps({"medical_records": count}, ensure_ascii=False)
        elif query_type == "recent":
            from datetime import datetime, timedelta

            week_ago = datetime.now() - timedelta(days=7)
            count = (
                db.query(DetectionTask)
                .filter(
                    DetectionTask.created_at >= week_ago,
                    DetectionTask.status == "completed",
                )
                .count()
            )
            total_lesions = (
                db.query(DetectionTask)
                .filter(
                    DetectionTask.created_at >= week_ago,
                    DetectionTask.status == "completed",
                )
                .all()
            )
            lesion_sum = sum(t.total_objects or 0 for t in total_lesions)
            return json.dumps(
                {"recent_7days_detections": count, "recent_7days_lesions": lesion_sum},
                ensure_ascii=False,
            )
        elif query_type == "lesions":
            tasks = (
                db.query(DetectionTask)
                .filter(DetectionTask.status == "completed")
                .all()
            )
            from app.services.detection_service import CLASS_NAMES_CN

            stats = {}
            for t in tasks:
                for r in t.results:
                    cn = r.class_name_cn or r.class_name
                    stats[cn] = stats.get(cn, 0) + 1
            return json.dumps({"lesion_distribution": stats}, ensure_ascii=False)
        elif query_type == "my_patients":
            if not user or user.user_type not in ("doctor", "admin"):
                return json.dumps({"message": "仅医生/管理员可查看"}, ensure_ascii=False)
            if user.user_type == "admin":
                profiles = db.query(PatientProfile).all()
            else:
                subq = (
                    db.query(DoctorPatientRelation.patient_id)
                    .filter(
                        DoctorPatientRelation.doctor_id == user.id,
                        DoctorPatientRelation.relation_status == "active",
                    )
                    .subquery()
                )
                profiles = (
                    db.query(PatientProfile)
                    .filter(PatientProfile.user_id.in_(db.query(subq.c.patient_id)))
                    .all()
                )
            items = [
                {
                    "code": p.patient_code,
                    "name": p.real_name or "-",
                    "age": p.age,
                    "gender": p.gender,
                }
                for p in profiles
            ]
            return json.dumps({"patients": items, "count": len(items)}, ensure_ascii=False)
        elif query_type == "my_records":
            if not user:
                return json.dumps({"message": "未登录"}, ensure_ascii=False)
            profile = (
                db.query(PatientProfile)
                .filter(PatientProfile.user_id == user.id)
                .first()
            )
            if not profile:
                return json.dumps({"message": "未找到档案"}, ensure_ascii=False)
            records = (
                db.query(MedicalRecord)
                .filter(MedicalRecord.patient_profile_id == profile.id)
                .order_by(MedicalRecord.visit_date.desc().nullslast())
                .all()
            )
            items = [
                {
                    "type": r.record_type,
                    "date": str(r.visit_date) if r.visit_date else "",
                    "chief": r.chief_complaint or "",
                    "status": r.record_status,
                }
                for r in records
            ]
            return json.dumps({"records": items, "count": len(items)}, ensure_ascii=False)
        else:
            return json.dumps({"error": f"未知查询类型: {query_type}"}, ensure_ascii=False)
    finally:
        db.close()


@tool
def generate_report(task_id: int = 0) -> str:
    """为指定检测任务生成结构化的胸部X光影像诊断报告。

    如不指定task_id，默认使用最近一次检测结果。
    报告包含：患者信息、检出病灶详情、AI分析意见、风险评级、临床建议。

    Args:
        task_id: 检测任务ID（可选，默认使用最近一次完成的检测）

    Returns:
        结构化诊断报告（Markdown格式）
    """
    from app.database.session import SessionLocal
    from app.entity.db_models import DetectionTask, PatientProfile

    db = SessionLocal()
    try:
        if task_id > 0:
            task = db.query(DetectionTask).filter(DetectionTask.id == task_id).first()
        else:
            task = (
                db.query(DetectionTask)
                .filter(DetectionTask.status == "completed")
                .order_by(DetectionTask.created_at.desc())
                .first()
            )

        if not task:
            return json.dumps(
                {"error": "未找到检测记录，请先进行检测"}, ensure_ascii=False
            )

        # 查患者信息
        patient_info = ""
        if task.patient_profile_id:
            profile = (
                db.query(PatientProfile)
                .filter(PatientProfile.id == task.patient_profile_id)
                .first()
            )
            if profile:
                patient_info = (
                    f"- 患者编号: {profile.patient_code}\n"
                    f"- 性别: {profile.gender or '未知'}  年龄: {profile.age or '未知'}\n"
                    f"- 科室: {profile.department or '未知'}\n"
                )

        # 病灶列表
        lesion_list = ""
        for r in task.results:
            cn = r.class_name_cn or r.class_name
            lesion_list += f"| {cn} | {r.confidence:.0%} | {r.bbox} |\n"

        report = f"""# 胸部X光影像诊断报告

## 基本信息
- 报告时间: {task.completed_at or task.created_at}
- 检测类型: {task.task_type}
{patient_info}

## 检测结果
- 检出病灶总数: {task.total_objects}
- 推理耗时: {task.total_inference_time:.0f}ms

| 病灶类型 | 置信度 | 位置坐标 |
|----------|--------|----------|
{lesion_list}

## AI 综合分析
{task.analysis_report or "暂无AI分析"}

## 风险评级
**{task.risk_level or "未评估"}**

## 建议
{task.analysis_suggestion or "请结合临床症状综合判断，必要时进一步检查。"}
---
*本报告由 ChestVision AI 辅助生成，仅供医生参考，不作为最终诊断依据。*
"""
        return report
    finally:
        db.close()


# 系统工具列表
SYSTEM_TOOLS = [
    query_system_info,
    generate_report,
]
