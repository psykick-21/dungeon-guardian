from typing import TypedDict, Literal
from enum import Enum

class WorldState(TypedDict):
    "Defines the structure for the world state"
    health: int
    stamina: int
    potionCount: int
    treasureThreatLevel: Literal['low', 'medium', 'high']
    enemyNearby: bool
    enemyLevel: Literal['very_low', 'low', 'medium', 'high', 'very_high', None]
    isInSafeZone: bool
    isBackup: bool
    treasureHealth: int
    comfyActions: int


class Goals(TypedDict):
    primaryGoal: str
    secondaryGoal: str


class Goal(Enum):
    "Enum for the goals of the agent"
    SURVIVE = "survive"
    ELIMINATE_THREAT = "eliminate_threat"
    PROTECT_TREASURE = "protect_treasure"
    PREPARE_FOR_BATTLE = "prepare_for_battle"


# print(Goal._member_names_)