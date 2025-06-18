from typing import TypedDict, Union, Annotated, List, Dict, Any
import operator
from ..type import WorldState


class AgentState(TypedDict):
    messages: Annotated[List[Dict[str, Any]], operator.add]
    currentWorldState: WorldState
    previousWorldState: WorldState
    primaryGoal: str
    secondaryGoal: str
    goalJustification: str
    actionFailureSuggestions: Union[str, None]
    actionSequence: list[str]
    plannerJustification: str
    failureOccurred: bool
    failureReason: str
    successOccurred: bool
    endReason: str
    actionFailed: bool
    iterations: int
    