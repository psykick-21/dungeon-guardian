from typing import TypedDict, Union, Sequence, Annotated
from langchain_core.messages import BaseMessage
import operator
from .type import WorldState, Goals


class AgentState(TypedDict):
    current_world_state: WorldState
    previous_world_state: WorldState
    goals: Goals
    suggestions: Union[str, None]
    goal_justification: str
    action_sequence: list[str]
    planner_justification: str
    