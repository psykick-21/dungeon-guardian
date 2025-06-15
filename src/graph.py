from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .states import AgentState
# from .structs import 
from .nodes import (
    goal_generator_node,
    planner_node
)
from .type import WorldState



builder = StateGraph(AgentState)

builder.add_node("goal_generator", goal_generator_node)
builder.add_node("planner", planner_node)

builder.add_edge(START, "goal_generator")
builder.add_edge("goal_generator", "planner")
builder.add_edge("planner", END)

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
        isBackup=False
    )
    result = graph.invoke({"current_world_state": world_state})
    print(result)