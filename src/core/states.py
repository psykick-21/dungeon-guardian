from typing import TypedDict, Union, Sequence, Annotated
from langchain_core.messages import BaseMessage
import operator
from ..type import WorldState


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_world_state: WorldState
    previous_world_state: Union[WorldState, None] = None
    