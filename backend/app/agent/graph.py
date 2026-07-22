"""
LangGraph 多 Agent 工作流 — 胸片X光智能分析系统

构建基于 LangGraph 的多智能体协作图（StateGraph）。

工作流拓扑：
                    ┌─────────────┐
                    │   START     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Supervisor │  ← 任务路由
                    └──────┬──────┘
                           │
           ┌───────┬───────┼───────┬───────┐
           ▼       ▼       ▼       ▼       ▼
       ┌──────┐┌──────┐┌──────┐┌──────┐┌──────────┐
       │detect││diagno││report││  qa  ││summarize │
       └──┬───┘└──┬───┘└──┬───┘└──┬───┘└────┬─────┘
          │       │       │       │         │
          └───────┴───────┴───────┴─────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    END      │
                    └─────────────┘

路由规则：
  - detection → diagnosis（自动衔接）
  - diagnosis → summarize
  - report    → summarize
  - qa        → summarize
  - summarize → END
  - FINISH    → END
"""

from typing import Literal

from langgraph.graph import END, StateGraph

from app.agent.nodes import (
    detection_node,
    diagnosis_node,
    qa_node,
    report_node,
    summarize_node,
)
from app.agent.state import MultiAgentState
from app.agent.supervisor import SupervisorAgent
from app.core.logger import get_logger

logger = get_logger(__name__)


def build_agent_graph(llm=None):
    """构建多 Agent 协作图

    Args:
        llm: LLM 实例（可选，不传则各节点内部自行创建）

    Returns:
        编译后的 LangGraph StateGraph
    """
    if llm is None:
        from app.agent.detection_agent import create_llm
        llm = create_llm()

    supervisor = SupervisorAgent(llm)

    # ── 创建状态图 ──
    workflow = StateGraph(MultiAgentState)

    # ── 注册节点 ──
    # Supervisor 路由节点
    workflow.add_node("supervisor", supervisor.route)

    # 专业 Agent 节点
    workflow.add_node("detection", _make_node_async(detection_node, llm))
    workflow.add_node("diagnosis", _make_node_async(diagnosis_node, llm))
    workflow.add_node("report", _make_node_async(report_node, llm))
    workflow.add_node("qa", _make_node_async(qa_node, llm))
    workflow.add_node("summarize", _make_node_async(summarize_node, llm))

    # ── 设置入口 ──
    workflow.set_entry_point("supervisor")

    # ── 设置条件路由边 ──
    # Supervisor → 各专业 Agent（条件路由）
    workflow.add_conditional_edges(
        "supervisor",
        _route_decision,
        {
            "detection": "detection",
            "diagnosis": "diagnosis",
            "report": "report",
            "qa": "qa",
            "summarize": "summarize",
            "FINISH": END,
        },
    )

    # ── 各 Agent → 下一节点 ──
    # detection → diagnosis（检测完自动诊断）
    workflow.add_edge("detection", "diagnosis")
    # diagnosis → summarize
    workflow.add_edge("diagnosis", "summarize")
    # report → summarize
    workflow.add_edge("report", "summarize")
    # qa → summarize
    workflow.add_edge("qa", "summarize")
    # summarize → END
    workflow.add_edge("summarize", END)

    # ── 编译图 ──
    compiled_graph = workflow.compile()
    logger.info("Multi-Agent LangGraph 工作流构建完成")
    return compiled_graph


def _route_decision(state: dict) -> Literal[
    "detection", "diagnosis", "report", "qa", "summarize", "FINISH"
]:
    """从 state 中提取 Supervisor 的路由决策"""
    next_agent = state.get("next_agent", "summarize")
    valid_routes = ["detection", "diagnosis", "report", "qa", "summarize", "FINISH"]
    if next_agent not in valid_routes:
        logger.warning("未知路由: %s，降级为 summarize", next_agent)
        return "summarize"
    return next_agent  # type: ignore[return-value]


def _make_node_async(node_func, llm):
    """将节点函数包装为 async callable，注入 llm 参数"""
    async def wrapper(state: dict) -> dict:
        return await node_func(state, llm)
    return wrapper
