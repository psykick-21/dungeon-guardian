from typing import List


class Action:
    "Class for the actions of the agent"

    def __init__(
            self,
            name: str,
            preconditions: List[str],
            effects: str
    ):
        self.name = name
        self.preconditions = preconditions
        self.effects = effects

    def __str__(self):
        return f"Action(name={self.name}, preconditions={self.preconditions}, effects={self.effects})"
    
    def __repr__(self):
        return self.__str__()


actions = [
    Action(
        name = "heal_self",
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
        preconditions = [
            "lambda x: x['enemyNearby'] == True",
            """lambda x: x['health'] > (
                (10 if x['isBackup'] == True else 20) if x['enemyLevel'] == "very_low" else
                (15 if x['isBackup'] == True else 25) if x['enemyLevel'] == "low" else
                (20 if x['isBackup'] == True else 35) if x['enemyLevel'] == "medium" else
                (25 if x['isBackup'] == True else 45) if x['enemyLevel'] == "high" else
                (30 if x['isBackup'] == True else 55) if x['enemyLevel'] == "very_high" else
                (15 if x['isBackup'] == True else 25)  # default fallback
            )""",
            "lambda x: x['stamina'] > 10"
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
        preconditions = [
            "lambda x: x['treasureThreatLevel'] != 'low'",
            "lambda x: x['stamina'] > 15"
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
        preconditions = [
            "lambda x: x['isInSafeZone'] == True",
            "lambda x: x['isBackup'] == False",
            "lambda x: x['stamina'] >= 40"
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
        preconditions = [
            "lambda x: x['isInSafeZone'] == True",
            "lambda x: x['stamina'] > 15",
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
        preconditions = [
            "lambda x: x['isInSafeZone'] == True",
            "lambda x: x['enemyNearby'] == False"
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
        preconditions = [
            "lambda x: x['isInSafeZone'] == True",
            "lambda x: x['stamina'] >= 10"
        ],
        effects = """{
    'isInSafeZone': lambda x: False,
    'stamina': lambda x: x['stamina'] - 10
}"""
    )
]



actions_dict = {action.name: action for action in actions}