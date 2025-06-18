from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .states import AgentState
from .nodes import (
    goal_generator_node,
    planner_node,
    action_executor_node,
    check_success_conditions_node,
    logger_node,
    failure_analysis_node
)
from ..type import WorldState
from .routers import success_router
import uuid
import json


builder = StateGraph(AgentState)

builder.add_node("goal_generator", goal_generator_node)
builder.add_node("planner", planner_node)
builder.add_node("action_executor", action_executor_node)
builder.add_node("check_success_conditions", check_success_conditions_node)
builder.add_node("failure_analysis_node", failure_analysis_node)
builder.add_node("logger_node", logger_node)

builder.add_edge(START, "goal_generator")
builder.add_edge("goal_generator", "planner")
builder.add_edge("planner", "action_executor")
builder.add_edge("action_executor", "check_success_conditions")
builder.add_conditional_edges("check_success_conditions", success_router)
builder.add_edge("failure_analysis_node", "logger_node")
builder.add_edge("logger_node", END)

graph = builder.compile(checkpointer=MemorySaver())