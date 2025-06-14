from enum import Enum
from typing import List
from dataclasses import dataclass



@dataclass
class Action:
    "Class for the actions of the agent"

    def __init__(
            self,
            name: str,
            preconditions: List[str],
            effects: List[str]
    ):
        self.preconditions = preconditions
        self.effects = effects


actions = [
    Action(
        name = "heal_self",
        preconditions = ["potion_count > 0", "is_in_safe_zone == True"],
        effects = ["health += 30", "potion_count -= 1"]
    ),
    Action(
        name = "attack_enemy",
        preconditions = ["enemy_nearby == True", "health > 20", "stamina > 10"],
        effects = [
            """
            if enemy_level == "very_low":
                health -= 10,
                enemy_level = None
            elif enemy_level == "low":
                health -= 30
            elif enemy_level == "medium":
                health -= 50
            elif enemy_level == "high":
                health -= 70
            elif enemy_level == "very_high":
                health -= 90
                enemy_level = None
            else:
                pass
            """,
            "enemy_nearby = False",
            "enemy_level = None",
            "stamina -= 10"
        ]
    ),
    Action(
        name = "retreat",
        preconditions = ["enemy_nearby == True", "is_in_safe_zone == False"],
        effects = [
            "enemy_nearby = False",
            "is_in_safe_zone = True",
            "stamina += 10"
        ]
    ),
    Action(
        name = "defend_treasure",
        preconditions = ["treasure_threat_level != 'low'"],
        effects = [
            """
            if treasure_threat_level == "medium":
                treasure_threat_level = "high"
            elif treasure_threat_level == "high":
                treasure_threat_level = "very_high"
            else:
                pass
            """,
            "stamina -= 10"
        ]
    ),
    Action(
        name = "call_backup",
        preconditions = ["is_in_safe_zone == True", "is_backup == False"],
        effects = [
            "is_backup = True",
            "stamina -= 20"
        ]
    ),
    Action(
        name = "search_for_potion",
        preconditions = ["is_in_safe_zone == True", "stamina > 10"],
        effects = [
            "potion_count += 1",
            "stamina -= 10",
        ]
    )
]