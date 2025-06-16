from typing import List


class Action:
    "Class for the actions of the agent"

    def __init__(
            self,
            name: str,
            preconditions: List[str],
            effects: str,
            description: str
    ):
        self.name = name
        self.preconditions = preconditions
        self.effects = effects
        self.description = description

    def __str__(self):
        return f"Action(name={self.name}, description={self.description}, preconditions={self.preconditions}, effects={self.effects})"
    
    def __repr__(self):
        return self.__str__()


action_pool = [
    Action(
        name = "heal_self",
        description = "Heal yourself using a potion. This action requires you to have at least one potion and be in a safe zone. When used, it will increase your health by 25 points (up to a maximum of 100), consume one potion, and count as a 'comfy' action. If you accumulate 2 or more comfy actions, the enemy level will increase by one level (from very_low to low, low to medium, etc.) and your comfy action count will reset. Additionally, if you're in a safe zone and an enemy is nearby, the treasure's health will decrease by 10 points.",
        preconditions = [
            lambda x: x['potionCount'] > 0,
            lambda x: x['isInSafeZone'] == True
        ],
        effects = {
            'health': lambda x: min(100, x['health'] + 25),
            'potionCount': lambda x: x['potionCount'] - 1,
            'enemyLevel': lambda x: (
                "high" if x["enemyLevel"] == "medium" else
                "very_high" if x["enemyLevel"] == "high" else
                "medium" if x["enemyLevel"] == "low" else
                "low" if x["enemyLevel"] == "very_low" else
                x["enemyLevel"]
            ) if x['comfyActions'] >= 2 else x["enemyLevel"],
            'comfyActions': lambda x: max(0, x['comfyActions'] + 1 - 2) if x['comfyActions'] >= 2 else x['comfyActions'] + 1,
            'treasureHealth': lambda x: max(0, x['treasureHealth'] - 10) if x['isInSafeZone'] == True and x['enemyNearby'] == True else x['treasureHealth']
        }
    ),
    Action(
        name = "attack_enemy",
        description = "Attack the enemy. This action requires an enemy to be nearby. When used, it will decrease your health based on the enemy level (with backup: 5 for very_low, 10 for low, 15 for medium, 20 for high, 25 for very_high; without backup: 10 for very_low, 20 for low, 30 for medium, 40 for high, 50 for very_high). It will also decrease your stamina by 15 points, set enemyNearby to False, and set enemyLevel to None.",
        preconditions = [
            lambda x: x['enemyNearby'] == True,
        ],
        effects = {
            'health': lambda x: x['health'] - (
                (5 if x['isBackup'] == True else 10) if x['enemyLevel'] == 'very_low' else
                (10 if x['isBackup'] == True else 20) if x['enemyLevel'] == 'low' else
                (15 if x['isBackup'] == True else 30) if x['enemyLevel'] == 'medium' else
                (20 if x['isBackup'] == True else 40) if x['enemyLevel'] == 'high' else
                (25 if x['isBackup'] == True else 50) if x['enemyLevel'] == 'very_high' else
                0
            ),
            'enemyNearby': lambda x: False,
            'enemyLevel': lambda x: None,
            'stamina': lambda x: x['stamina'] - 15
        }
    ),
    Action(
        name = "retreat",
        description = "Retreat to the safe zone. This action requires you to not be in a safe zone. When used, it will move you to a safe zone (sets isInSafeZone to True) and decrease your stamina by 5 points.",
        preconditions = [
            lambda x: x['isInSafeZone'] == False
        ],
        effects = {
            'isInSafeZone': lambda x: True,
            'stamina': lambda x: x['stamina'] - 5
        }
    ),
    Action(
        name = "defend_treasure",
        description = "Defend the treasure. This action requires the treasure threat level to not be 'low'. When used, it will decrease the treasure threat level by one step (from high to medium, or from medium to low) and decrease your stamina by 20 points.",
        preconditions = [
            lambda x: x['treasureThreatLevel'] != 'low'
        ],
        effects = {
            'treasureThreatLevel': lambda x: (
                "medium" if x["treasureThreatLevel"] == "high" else
                "low" if x["treasureThreatLevel"] == "medium" else
                x["treasureThreatLevel"]
            ),
            'stamina': lambda x: x['stamina'] - 20
        }
    ),
    Action(
        name = "call_backup",
        description = "Call for backup. This action requires you to be in a safe zone and not already have backup. When used, it will set isBackup to True and decrease your stamina by 40 points. If you have 2 or more comfy actions accumulated, it will increase the enemy level by one step (from very_low to low, low to medium, etc.) and reset your comfy action count. Additionally, if an enemy is nearby while in the safe zone, the treasure's health will decrease by 10 points.",
        preconditions = [
            lambda x: x['isInSafeZone'] == True,
            lambda x: x['isBackup'] == False
        ],
        effects = {
            'isBackup': lambda x: True,
            'stamina': lambda x: x['stamina'] - 40,
            'enemyLevel': lambda x: (
                "high" if x["enemyLevel"] == "medium" else
                "very_high" if x["enemyLevel"] == "high" else
                "medium" if x["enemyLevel"] == "low" else
                "low" if x["enemyLevel"] == "very_low" else
                x["enemyLevel"]
            ) if x['comfyActions'] >= 2 else x["enemyLevel"],
            'comfyActions': lambda x: max(0, x['comfyActions'] + 1 - 2) if x['comfyActions'] >= 2 else x['comfyActions'] + 1,
            'treasureHealth': lambda x: max(0, x['treasureHealth'] - 10) if x['isInSafeZone'] == True and x['enemyNearby'] == True else x['treasureHealth']
        }
    ),
    Action(
        name = "search_for_potion",
        description = "Search for a potion. This action requires you to be in a safe zone and have less than 2 potions. When used, it will increase your potion count by 1 and decrease your stamina by 15 points. If you have 2 or more comfy actions accumulated, it will increase the enemy level by one step (from very_low to low, low to medium, etc.) and reset your comfy action count. Additionally, if an enemy is nearby while in the safe zone, the treasure's health will decrease by 10 points.",
        preconditions = [
            lambda x: x['isInSafeZone'] == True,
            lambda x: x['potionCount'] < 2
        ],
        effects = {
            'potionCount': lambda x: x['potionCount'] + 1,
            'stamina': lambda x: x['stamina'] - 15,
            'enemyLevel': lambda x: (
                "high" if x["enemyLevel"] == "medium" else
                "very_high" if x["enemyLevel"] == "high" else
                "medium" if x["enemyLevel"] == "low" else
                "low" if x["enemyLevel"] == "very_low" else
                x["enemyLevel"]
            ) if x['comfyActions'] >= 2 else x["enemyLevel"],
            'comfyActions': lambda x: max(0, x['comfyActions'] + 1 - 2) if x['comfyActions'] >= 2 else x['comfyActions'] + 1,
            'treasureHealth': lambda x: max(0, x['treasureHealth'] - 10) if x['isInSafeZone'] == True and x['enemyNearby'] == True else x['treasureHealth']
        }
    ),
    Action(
        name = "rest",
        description = "Rest to recover health and stamina. This action requires you to be in a safe zone. When used, it will increase your stamina by 25 points (up to a maximum of 100) and your health by 15 points (up to a maximum of 100). If you have 2 or more comfy actions accumulated, it will increase the enemy level by one step (from very_low to low, low to medium, etc.) and reset your comfy action count. Additionally, if an enemy is nearby while in the safe zone, the treasure's health will decrease by 10 points.",
        preconditions = [
            lambda x: x['isInSafeZone'] == True
        ],
        effects = {
            'stamina': lambda x: min(100, x['stamina'] + 25),
            'health': lambda x: min(100, x['health'] + 15),
            'enemyLevel': lambda x: (
                "high" if x["enemyLevel"] == "medium" else
                "very_high" if x["enemyLevel"] == "high" else
                "medium" if x["enemyLevel"] == "low" else
                "low" if x["enemyLevel"] == "very_low" else
                x["enemyLevel"]
            ) if x['comfyActions'] >= 2 else x["enemyLevel"],
            'comfyActions': lambda x: max(0, x['comfyActions'] + 1 - 2) if x['comfyActions'] >= 2 else x['comfyActions'] + 1,
            'treasureHealth': lambda x: max(0, x['treasureHealth'] - 10) if x['isInSafeZone'] == True and x['enemyNearby'] == True else x['treasureHealth']
        }
    ),
    Action(
        name = "return_to_treasure",
        description = "Return to the treasure. This action requires you to be in a safe zone. When used, it will move you out of the safe zone (sets isInSafeZone to False) and decrease your stamina by 10 points.",
        preconditions = [
            lambda x: x['isInSafeZone'] == True
        ],
        effects = {
            'isInSafeZone': lambda x: False,
            'stamina': lambda x: x['stamina'] - 10
        }
    )
]


action_descriptions = [
    {
        "name": action.name,
        "description": action.description
    } for action in action_pool
]

actions_dict = {
    action.name: {
        "preconditions": action.preconditions,
        "effects": action.effects
    } for action in action_pool
}