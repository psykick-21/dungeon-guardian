from .states import AgentState


def success_router(state: AgentState):
    """
    Route the agent workflow based on whether success has occurred.
    
    This router determines the next node in the agent workflow by checking if the agent
    has successfully completed its mission. If success has occurred, it routes to the
    failure analysis node for final processing. Otherwise, it continues the main loop
    by routing back to the goal generator.
    
    Args:
        state (AgentState): The current state of the agent containing success status
                           and other workflow information.
    
    Returns:
        str: The name of the next node to execute:
            - 'failure_analysis_node' if success has occurred
            - 'goal_generator' if success has not occurred
    """
    
    if state['successOccurred']:
        return 'failure_analysis_node'
    else:
        return 'goal_generator'