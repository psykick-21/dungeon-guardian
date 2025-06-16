from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .states import AgentState
# from .structs import 
from .nodes import (
    goal_generator_node,
    planner_node,
    action_executor_node,
    check_success_conditions_node,
    logger_node,
    failure_analysis_node
)
from .type import WorldState
from .routers import success_router



builder = StateGraph(AgentState)

builder.add_node("goal_generator", goal_generator_node)
builder.add_node("planner", planner_node)
builder.add_node("action_executor", action_executor_node)
builder.add_node("check_success_conditions", check_success_conditions_node)
builder.add_node("logger_node", logger_node)
builder.add_node("failure_analysis_node", failure_analysis_node)

builder.add_edge(START, "goal_generator")
builder.add_edge("goal_generator", "planner")
builder.add_edge("planner", "action_executor")
builder.add_edge("action_executor", "check_success_conditions")
builder.add_conditional_edges("check_success_conditions", success_router)
builder.add_edge("logger_node", "failure_analysis_node")
builder.add_edge("failure_analysis_node", END)

graph = builder.compile()



if __name__ == "__main__":
    world_state = WorldState(
        health=80,
        stamina=80,
        potionCount=2,
        treasureThreatLevel="high",
        enemyNearby=True,
        enemyLevel="very_high",
        isInSafeZone=False,
        isBackup=False,
        treasureHealth=100,
        comfyActions=0
    )
    
    events = graph.stream({"current_world_state": world_state}, {"recursion_limit": 100})

    for event in events:
        if "goal_generator" in event:
            print("<<< GOAL GENERATOR >>>")
            print(f"Primary goal: {event['goal_generator']['goals']['primaryGoal']}")
            print(f"Secondary goal: {event['goal_generator']['goals']['secondaryGoal']}")
            print(f"Justification: {event['goal_generator']['goal_justification']}")
            print(f"Action failure suggestions: {event['goal_generator']['actionFailureSuggestions']}")
            print("--------------------------------\n\n")

        elif "planner" in event:

            print("<<< PLANNER >>>")
            print(f"Action sequence: {event['planner']['action_sequence']}")
            print("--------------------------------\n\n")

        elif "action_executor" in event:
            print("<<< ACTION EXECUTOR >>>")
            print(event["action_executor"]["messages"][-1].content)
            print("--------------------------------\n\n")

        elif "check_success_conditions" in event:
            print("<<< CHECK SUCCESS CONDITIONS >>>")
            print(event["check_success_conditions"]["messages"][-1].content )
            print("--------------------------------\n\n")

        elif "logger_node" in event:
            print("Logging event...")

        elif "failure_analysis_node" in event:
            print("<<< FAILURE ANALYSIS >>>")
            print(event["failure_analysis_node"]["messages"][-1].content)
            print("--------------------------------\n\n")
        
        else:
            print(event)