from .states import AgentState


def success_router(state: AgentState):
    
    if state['success_occurred']:
        return 'logger_node'
    else:
        return 'goal_generator'