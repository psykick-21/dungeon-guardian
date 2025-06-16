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


actions = [
    Action(
        name = "heal_self",
        description = "Heal yourself by using a potion. This action will increase your health by 25 points. It will also decrease your potion count by 1. It will also decrease your stamina by 10 points. It will also increase your comfy actions by 1. It will also increase your enemy level by 1 level if you have 2 or more comfy actions accumulated It will also decrease your treasure health by 10 points if the enemy is nearby.",
        preconditions = [
            "lambda x: x['potionCount'] > 0",
            "lambda x: x['isInSafeZone'] == True"
        ],
        effects = """{
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
}"""
    ),
    Action(
        name = "attack_enemy",
        description = "Attack the enemy. This action will decrease your health by a certain amount based on the enemy level. It will also decrease your stamina by 15 points. It will also set the enemyNearby to False. It will also set the enemyLevel to None.",
        preconditions = [
            "lambda x: x['enemyNearby'] == True",
        ],
        effects = """{
    'health': lambda x: x['health'] - (
        (5 if x["isBackup"] == True else 10) if x["enemyLevel"] == "very_low" else
        (10 if x["isBackup"] == True else 20) if x["enemyLevel"] == "low" else
        (15 if x["isBackup"] == True else 30) if x["enemyLevel"] == "medium" else
        (20 if x["isBackup"] == True else 40) if x["enemyLevel"] == "high" else
        (25 if x["isBackup"] == True else 50) if x["enemyLevel"] == "very_high" else
        0
    ),
    'enemyNearby': lambda x: False,
    'enemyLevel': lambda x: None,
    'stamina': lambda x: x['stamina'] - 15
}"""
    ),
    Action(
        name = "retreat",
        description = "Retreat to the safe zone. This action will set the isInSafeZone to True. It will also decrease your stamina by 5 points.",
        preconditions = [
            "lambda x: x['isInSafeZone'] == False"
        ],
        effects = """{
    'isInSafeZone': lambda x: True,
    'stamina': lambda x: x['stamina'] - 5
}"""
    ),
    Action(
        name = "defend_treasure",
        description = "Defend the treasure. It will decrease your stamina by 20 points. It will also decrease your treasure threat level by 1 level.",
        preconditions = [
            "lambda x: x['treasureThreatLevel'] != 'low'",
        ],
        effects = """{
    'treasureThreatLevel': lambda x: (
        "medium" if x["treasureThreatLevel"] == "high" else
        "low" if x["treasureThreatLevel"] == "medium" else
        x["treasureThreatLevel"]
    ),
    'stamina': lambda x: x['stamina'] - 20
}"""
    ),
    Action(
        name = "call_backup",
        description = "Call for backup. This action will set the isBackup to True. It will also decrease your stamina by 40 points. It will also increase your enemy level by 1 level if you have 2 or more comfy actions accumulated. It will also decrease your treasure health by 10 points if the enemy is nearby.",
        preconditions = [
            "lambda x: x['isInSafeZone'] == True",
            "lambda x: x['isBackup'] == False",
        ],
        effects = """{
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
}"""
    ),
    Action(
        name = "search_for_potion",
        description = "Search for a potion. This action will increase your potion count by 1. It will also decrease your stamina by 15 points. It will also increase your enemy level by 1 level if you have 2 or more comfy actions accumulated. It will also decrease your treasure health by 10 points if the enemy is nearby.",
        preconditions = [
            "lambda x: x['isInSafeZone'] == True",
            "lambda x: x['potionCount'] < 2"
        ],
        effects = """{
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
}"""
    ),
    Action(
        name = "rest",
        description = "Rest. This action will increase your stamina by 25 points. It will also increase your health by 15 points. It will also increase your enemy level by 1 level if you have 2 or more comfy actions accumulated. It will also decrease your treasure health by 10 points if the enemy is nearby.",
        preconditions = [
            "lambda x: x['isInSafeZone'] == True",
        ],
        effects = """{
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
}"""
    ),
    Action(
        name = "return_to_treasure",
        description = "Return to the treasure. This action will set the isInSafeZone to False. It will also decrease your stamina by 10 points.",
        preconditions = [
            "lambda x: x['isInSafeZone'] == True",
        ],
        effects = """{
    'isInSafeZone': lambda x: False,
    'stamina': lambda x: x['stamina'] - 10
}"""
    )
]



actions_dict = {action.name: action for action in actions}