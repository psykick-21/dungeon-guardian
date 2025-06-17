from .states import AgentState


def success_router(state: AgentState):
    
    if state['successOccurred']:
        return 'logger_node'
    else:
        return 'goal_generator'