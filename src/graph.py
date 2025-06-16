from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .states import AgentState
# from .structs import 
from .nodes import (
    goal_generator_node,
    planner_node,
    action_executor_node,
    check_success_conditions_node,
    logger_node
)
from .type import WorldState
from .routers import success_router



builder = StateGraph(AgentState)

builder.add_node("goal_generator", goal_generator_node)
builder.add_node("planner", planner_node)
builder.add_node("action_executor", action_executor_node)
builder.add_node("check_success_conditions", check_success_conditions_node)
builder.add_node("logger", logger_node)

builder.add_edge(START, "goal_generator")
builder.add_edge("goal_generator", "planner")
builder.add_edge("planner", "action_executor")
builder.add_edge("action_executor", "check_success_conditions")
builder.add_edge("check_success_conditions", "logger")
builder.add_edge("logger", END)
# builder.add_conditional_edges("check_success_conditions", success_router)

graph = builder.compile()



if __name__ == "__main__":
    world_state = WorldState(
        health=20,
        stamina=5,
        potionCount=0,
        treasureThreatLevel="medium", 
        enemyNearby=True,
        enemyLevel="medium",
        isInSafeZone=False,
        isBackup=False,
        treasureHealth=60,
        comfyActions=1
    )
    result = graph.invoke({"current_world_state": world_state})
    print(result)