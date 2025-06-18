from src.agent.graph import graph
from src.type import WorldState
import uuid
import json

# Initialize the world state here
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


if __name__ == "__main__":

    events = graph.stream(
        {"currentWorldState": world_state},
        {
            "recursion_limit": 100, 
            "configurable": {"thread_id": str(uuid.uuid4())}
        }
    )

    for event in events:
        if "goal_generator" in event:
            print("<<< WORLD STATE >>>")
            print(json.dumps(event["goal_generator"]["currentWorldState"], indent=4))
            print("--------------------------------\n\n")
            
            print("<<< GOAL GENERATOR >>>")
            print(f"Primary goal: {event['goal_generator']['primaryGoal']}")
            print(f"Secondary goal: {event['goal_generator']['secondaryGoal']}")
            print(f"Justification: {event['goal_generator']['goalJustification']}")
            print(f"Action failure suggestions: {event['goal_generator']['actionFailureSuggestions']}")
            print("--------------------------------\n\n")

        elif "planner" in event:

            print("<<< PLANNER >>>")
            print(f"Action sequence: {event['planner']['actionSequence']}")
            print("--------------------------------\n\n")

        elif "action_executor" in event:
            print("<<< ACTION EXECUTOR >>>")
            print(event["action_executor"]["messages"][-1]["gameMessage"])
            print("--------------------------------\n\n")

        elif "check_success_conditions" in event:
            print("<<< CHECK SUCCESS CONDITIONS >>>")
            print(event["check_success_conditions"]["messages"][-1]["gameMessage"])
            print("--------------------------------\n\n")

        elif "logger_node" in event:
            print("Logging event...")

        elif "failure_analysis_node" in event:
            print("<<< FAILURE ANALYSIS >>>")
            print(event["failure_analysis_node"]["messages"][-1]["learner"])
            print("--------------------------------\n\n")
        
        else:
            print(event)