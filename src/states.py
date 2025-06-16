from typing import TypedDict, Union, Annotated, List
from langchain_core.messages import BaseMessage
import operator
from .type import WorldState, Goals


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    current_world_state: WorldState
    previous_world_state: WorldState
    goals: Goals
    actionFailureSuggestions: Union[str, None]
    goal_justification: str
    action_sequence: list[str]
    planner_justification: str
    failure_occurred: bool
    failure_reason: str
    success_occurred: bool
    end_reason: str
    action_failed: bool
    iterations: int
    