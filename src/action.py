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
        preconditions = ["potionCount > 0", "isInSafeZone == True"],
        effects = [
            "health = min(100, health + 25)",
            "potionCount -= 1"
        ]
    ),
    Action(
        name = "attack_enemy",
        preconditions = ["enemyNearby == True", "health > (15 if isBackup == True else 25)", "stamina > 10"],
        effects = [
            "if enemyLevel == 'very_low': health -= (5 if isBackup == True else 10)",
            "if enemyLevel == 'low': health -= (10 if isBackup == True else 20)",
            "if enemyLevel == 'medium': health -= (15 if isBackup == True else 30)",
            "if enemyLevel == 'high': health -= (20 if isBackup == True else 40)",
            "if enemyLevel == 'very_high': health -= (25 if isBackup == True else 50)",
            "enemyNearby = False",
            "enemyLevel = None",
            "stamina -= 15"
        ]
    ),
    Action(
        name = "retreat",
        preconditions = ["enemyNearby == True", "isInSafeZone == False"],
        effects = [
            "enemyNearby = False",
            "isInSafeZone = True",
            "stamina += 5"
        ]
    ),
    Action(
        name = "defend_treasure",
        preconditions = ["treasureThreatLevel != 'low'", "stamina > 15"],
        effects = [
            "if treasureThreatLevel == 'high': treasureThreatLevel = 'medium'",
            "if treasureThreatLevel == 'medium': treasureThreatLevel = 'low'",
            "stamina -= 20"
        ]
    ),
    Action(
        name = "call_backup",
        preconditions = ["isInSafeZone == True", "isBackup == False", "stamina >= 40"],
        effects = [
            "isBackup = True",
            "stamina -= 40"
        ]
    ),
    Action(
        name = "search_for_potion",
        preconditions = ["isInSafeZone == True", "stamina > 15", "potionCount < 2"],
        effects = [
            "potionCount += 1",
            "stamina -= 15",
        ]
    ),
    Action(
        name = "rest",
        preconditions = ["isInSafeZone == True", "enemyNearby == False"],
        effects = [
            "stamina = min(100, stamina + 25)",
            "health = min(100, health + 15)"
        ]
    )
]