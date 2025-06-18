from src.agent.graph import graph
from src.type import WorldState
import uuid
import json

# Scenario 1: Low Health, No Healing Resources, Enemy Nearby
scenario_1 = WorldState(
    health=20,
    stamina=5,
    potionCount=0,
    treasureThreatLevel="medium",
    enemyNearby=True,
    enemyLevel="high",
    isInSafeZone=False,
    isBackup=False,
    treasureHealth=80,
    comfyActions=0
)

# Scenario 2: Healthy, Treasure Under Threat, Enemy Nearby
scenario_2 = WorldState(
    health=85,
    stamina=75,
    potionCount=1,
    treasureThreatLevel="high",
    enemyNearby=True,
    enemyLevel="medium",
    isInSafeZone=False,
    isBackup=False,
    treasureHealth=60,
    comfyActions=0
)

# Scenario 3: No Enemy Nearby, Low Stamina, Potion Available
scenario_3 = WorldState(
    health=70,
    stamina=15,
    potionCount=2,
    treasureThreatLevel="low",
    enemyNearby=False,
    enemyLevel="none",
    isInSafeZone=True,
    isBackup=False,
    treasureHealth=100,
    comfyActions=3
)

# Scenario 4: Out of Potions, Enemy Near, Treasure Safe
scenario_4 = WorldState(
    health=60,
    stamina=40,
    potionCount=0,
    treasureThreatLevel="low",
    enemyNearby=True,
    enemyLevel="medium",
    isInSafeZone=False,
    isBackup=False,
    treasureHealth=95,
    comfyActions=1
)

# Scenario 5: Critical Situation - Multiple Enemies, Low Resources
scenario_5 = WorldState(
    health=30,
    stamina=25,
    potionCount=1,
    treasureThreatLevel="very_high",
    enemyNearby=True,
    enemyLevel="very_high",
    isInSafeZone=False,
    isBackup=True,
    treasureHealth=40,
    comfyActions=0
)


if __name__ == "__main__":

    scenerios = [scenario_1, scenario_2, scenario_3, scenario_4, scenario_5]

    for world_state in scenerios:

        print(f"Running scenerio: {world_state}")

        results = graph.invoke(
            {"currentWorldState": world_state},
            {
                "recursion_limit": 100, 
                "configurable": {"thread_id": str(uuid.uuid4())}
            }
        )

        print(
            f"failureOccurred: {results["failureOccurred"]}\n\n"
            f"failureReason: {results["failureReason"]}\n\n"
            f"successOccurred: {results["successOccurred"]}\n\n"
            f"endReason: {results["endReason"]}\n\n"
            f"iterations: {results["iterations"]}\n\n"
            "--------------------------------\n\n"
        )