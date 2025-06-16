from .states import AgentState
from langgraph.graph import END


def success_router(state: AgentState):
    
    if state['success_occurred']:
        return END
    else:
        return 'goal_generator'