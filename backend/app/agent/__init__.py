"""
智能体模块 — 胸片X光智能分析系统

架构演进：
  Day 8:  单 Agent (ReAct) + 胸片检测工具
  Day 11: 多工具 Agent + 对话记忆 + RAG + SSE增强
  Day 12: LangGraph 多 Agent 协作架构（当前）

当前多 Agent 架构：
  Supervisor（路由）→ Detection / Diagnosis / Report / QA → Summarize（汇总输出）

模块组成：
  - state.py:      多 Agent 状态定义（MultiAgentState）
  - supervisor.py: Supervisor 路由 Agent（任务调度中心）
  - nodes.py:      各专业 Agent 节点（detection/diagnosis/report/qa/summarize）
  - graph.py:      LangGraph 工作流构建
  - prompts.py:    Prompt 模板集中管理
  - memory.py:     对话记忆管理（Redis）
  - detection_agent.py: 单 Agent 实现（兼容旧接口）
  - tools/:        工具集（检测/分析/知识库）
"""

from app.agent.state import MultiAgentState
from app.agent.supervisor import SupervisorAgent
from app.agent.graph import build_agent_graph
from app.agent.nodes import (
    detection_node,
    diagnosis_node,
    qa_node,
    report_node,
    summarize_node,
)

__all__ = [
    "MultiAgentState",
    "SupervisorAgent",
    "build_agent_graph",
    "detection_node",
    "diagnosis_node",
    "report_node",
    "qa_node",
    "summarize_node",
]
