from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import (
    ChatPromptTemplate, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate,
)
from langchain_core.messages import SystemMessage
from .states import AgentState
from ..configuration import Configuration
from ..utils import init_llm, create_agent, check_failure_conditions, check_success_conditions
from .prompts import (
    GOAL_GENERATOR_SYSTEM_PROMPT_TEMPLATE,
    PLANNER_SYSTEM_PROMPT_TEMPLATE,
    FAILURE_ANALYSIS_SYSTEM_PROMPT_TEMPLATE
)
from ..type import Goal
from .structs import (
    GoalGeneratorResponse,
    PlannerResponse,
    HistoricalLearnings
)
import os
from ..action import action_descriptions, actions_dict, action_failure_probability
import json
import random



def goal_generator_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Generate primary and secondary goals for the agent based on current world state and historical learnings.
    
    This node is responsible for analyzing the current world state and past failure experiences
    to generate appropriate primary and secondary goals for the agent. It loads historical
    learnings from previous failures to inform better goal setting and decision making.
    
    Args:
        state (AgentState): The current state of the agent containing world state, messages,
                           and other workflow information.
        config (RunnableConfig): Configuration object containing LLM provider settings,
                                model parameters, and learning path for historical data.
    
    Returns:
        AgentState: Updated agent state containing:
            - messages: Updated with current world state and goal generator response
            - currentWorldState: Preserved from input state
            - primaryGoal: Generated primary objective for the agent
            - secondaryGoal: Generated secondary objective for the agent
            - goalJustification: Reasoning behind the generated goals
    """
    
    configurable = Configuration.from_runnable_config(config)
    learning_path = configurable.learning_path

    if os.path.exists(os.path.join(learning_path, "historical_learnings.json")):
        with open(os.path.join(learning_path, "historical_learnings.json"), "r") as f:
            historical_learnings = json.load(f)
    else:
        historical_learnings = {}

    llm = init_llm(
        provider=configurable.provider,
        model=configurable.model,
        temperature=configurable.temperature
    )

    goal_generator_system_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(GOAL_GENERATOR_SYSTEM_PROMPT_TEMPLATE),
        SystemMessage(content=json.dumps(state['messages'])),
        HumanMessagePromptTemplate.from_template(
            template = """
            ## Current world state: \n{currentWorldState}\n
            ## Learnings from past failures: \n{historicalLearnings}\n
            """
        )
    ])

    goal_generator_agent = create_agent(
        llm=llm,
        prompt=goal_generator_system_prompt,
        output_structure=GoalGeneratorResponse
    )

    result = goal_generator_agent.invoke({**state, "historicalLearnings": historical_learnings})

    return {
        "messages": [
            {"worldState": state["currentWorldState"]},
            {"goalGenerator": {**result.model_dump()}}
        ],
        "currentWorldState": state["currentWorldState"],
        **result.model_dump()
    }



def planner_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Generate an action sequence plan based on the current world state and goals.
    
    This node creates a detailed action plan by analyzing the current world state,
    the agent's primary and secondary goals, and any previous action failure suggestions.
    It uses a language model to generate a sequence of actions that should help the
    agent achieve its objectives while considering past failures.
    
    Args:
        state (AgentState): The current state of the agent containing:
            - currentWorldState: Current state of the game world
            - primaryGoal: The agent's primary objective
            - secondaryGoal: The agent's secondary objective
            - actionFailureSuggestions: Suggestions from previous action failures
        config (RunnableConfig): Configuration containing LLM provider settings
    
    Returns:
        AgentState: Updated state containing:
            - messages: List with the planner's response added
            - actionSequence: Generated sequence of actions to execute
            - plannerJustification: Reasoning behind the generated plan
    """
    
    configurable = Configuration.from_runnable_config(config)
    
    llm = init_llm(
        provider=configurable.provider,
        model=configurable.model,
        temperature=configurable.temperature
    )
    
    planner_system_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(PLANNER_SYSTEM_PROMPT_TEMPLATE),
        HumanMessagePromptTemplate.from_template(
            template="""
            ## Current world state:\n{currentWorldState}\n
            ## Goals: \n{goals}\n
            ## Action failure reasons: \n{actionFailureSuggestions}\n
            """
        )
    ])

    planner_agent = create_agent(
        llm=llm,
        prompt=planner_system_prompt,
        output_structure=PlannerResponse
    )

    result = planner_agent.invoke({**state, "actions": action_descriptions, "goals": Goal._member_names_})

    return {
        "messages": [{"planner": {**result.model_dump()}}],
        **result.model_dump()
    }



def action_executor_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Execute a sequence of actions and update the world state accordingly.
    
    This node processes the planned action sequence from the planner, executing each action
    in order while checking preconditions and handling potential failures. It manages:
    - Action precondition validation
    - Probabilistic action failures
    - World state updates from action effects
    - Game failure condition checking
    - Action execution tracking
    
    The function will stop execution early if:
    - An action fails due to probability
    - An action's preconditions are not met
    - A game failure condition is triggered
    
    Args:
        state (AgentState): The current state of the agent containing:
            - currentWorldState: Current state of the game world
            - actionSequence: List of action names to execute in order
        config (RunnableConfig): Configuration containing execution settings
    
    Returns:
        AgentState: Updated state containing:
            - messages: List with game message describing execution results
            - currentWorldState: Updated world state after action execution
            - previousWorldState: World state before action execution
            - failureOccurred: Boolean indicating if game failure occurred
            - failureReason: Description of failure if one occurred
            - actionFailed: Boolean indicating if any action failed to execute
    """
    
    previous_world_state = state["currentWorldState"]
    current_world_state = state["currentWorldState"].copy()
    action_sequence = state["actionSequence"]
    
    executed_actions = []
    failure_occurred = False
    failure_reason = ""
    action_failed = False

    game_message = ""

    for action_name in action_sequence:

        # Handle action failure due to probability
        action_failure_probability_object = action_failure_probability.get(action_name, None)
        if action_failure_probability_object:
            if (random.random() < action_failure_probability_object["probability"]):
                action_failed = True
                game_message += f"Action {action_name} failed because of the following reason: {action_failure_probability_object['reason']}\n"
                game_message += f"Executed actions: {executed_actions}"
                for key, value in action_failure_probability_object["effects"].items():
                    current_world_state[key] = value(current_world_state)

                return {
                    "messages": [
                        {"gameMessage": game_message}
                    ],
                    "currentWorldState": current_world_state,
                    "previousWorldState": previous_world_state,
                    "failureOccurred": failure_occurred,
                    "failureReason": failure_reason,
                    "actionFailed": action_failed,
                }


        action_obj = actions_dict[action_name]
        preconditions_met = True
        
        for precondition in action_obj["preconditions"]:
            if not precondition(current_world_state):
                preconditions_met = False
                game_message += f"Action {action_name} failed because precondition is not met.\n"
                action_failed = True
                break

        if preconditions_met:
            for key, value in action_obj["effects"].items():
                current_world_state[key] = value(current_world_state)
            
            executed_actions.append(action_name)
            
            # Handle game failure due to failure conditions
            is_failed, reason = check_failure_conditions(current_world_state)
            if is_failed:
                failure_occurred = True
                failure_reason = reason
                game_message += f"You have failed due to the following reason: {reason}.\nPlease try again."

                return {
                    "messages": [
                        {"gameMessage": game_message}
                    ],
                    "currentWorldState": previous_world_state,
                    "previousWorldState": previous_world_state,
                    "failureOccurred": failure_occurred,
                    "failureReason": failure_reason,
                    "actionFailed": action_failed,
                }
                
        else:
            continue

    game_message += f"No game failure occurred.\n"
    game_message += f"Executed actions: {executed_actions}"


    return {
        "messages": [
            {"gameMessage": game_message}
        ],
        "currentWorldState": current_world_state,
        "previousWorldState": previous_world_state,
        "failureOccurred": failure_occurred,
        "failureReason": failure_reason,
        "actionFailed": action_failed,
    }
    


def check_success_conditions_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Check if the agent has achieved success conditions or if the game should end.
    
    This node evaluates the current world state to determine if the agent has successfully
    completed its mission. It also handles iteration limits and provides appropriate
    game messages based on the outcome.
    
    Args:
        state (AgentState): The current state of the agent containing world state,
                           iteration count, and other workflow information.
        config (RunnableConfig): Configuration object containing game settings
                                including total iteration limits.
    
    Returns:
        AgentState: Updated state containing:
            - messages: Game message indicating success, continuation, or timeout
            - successOccurred: Boolean indicating if success conditions were met
            - endReason: String describing why the game ended (success message or timeout)
    """

    configurable = Configuration.from_runnable_config(config)
    iterations = state.get("iterations", 0) + 1
    iterations_limit_reached = False
    
    game_message = ""
    is_successful, success_msg = check_success_conditions(state['currentWorldState'])
    
    if is_successful:
        game_message += f"Congratulations! {success_msg}\n"
        
        return {
            "messages": [
                {"gameMessage": game_message}
            ],
            "successOccurred": is_successful,
            "endReason": success_msg,
            "iterations": iterations,
            "iterationsLimitReached": iterations_limit_reached
        }
    
    else:
    
        if iterations >= configurable.total_iterations:
            iterations_limit_reached = True
            return {
                "messages": [
                    {"gameMessage": "You have run out of maximum permissible iterations. The game has ended without success or failure."}
                ],
                "successOccurred": is_successful,
                "endReason": "The game has run out of iterations.",
                "iterations": iterations,
                "iterationsLimitReached": iterations_limit_reached
            }
        
        game_message += f"The game is still running. Please continue.\n"
        return {
            "messages": [
                {"gameMessage": game_message}
            ],
            "successOccurred": is_successful,
            "endReason": success_msg,
            "iterations": iterations,
            "iterationsLimitReached": iterations_limit_reached
        }
    


def failure_analysis_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Analyze the completed episode and extract learnings for future improvement.
    
    This node performs post-episode analysis by examining the agent's performance,
    extracting key learnings from successes and failures, and updating the historical
    learnings database. It uses an LLM to analyze the episode messages and generate
    structured insights that can inform future agent behavior.
    
    Args:
        state (AgentState): The current state of the agent containing:
            - messages: Complete conversation history from the episode
            - successOccurred: Boolean indicating if the episode was successful
            - failureOccurred: Boolean indicating if the episode failed
            - endReason: String describing why the episode ended
        config (RunnableConfig): Configuration object containing:
            - learning_path: Directory path where learnings will be stored
            - provider: LLM provider to use for analysis
            - model: Specific model name for the LLM
            - temperature: Temperature setting for the LLM
    
    Returns:
        AgentState: Updated state containing:
            - messages: Analysis results with extracted learnings in structured format
    """
    
    configurable = Configuration.from_runnable_config(config)
    learning_path = configurable.learning_path

    os.makedirs(learning_path, exist_ok=True)

    if os.path.exists(os.path.join(learning_path, "historical_learnings.json")):
        with open(os.path.join(learning_path, "historical_learnings.json"), "r") as f:
            historical_learnings = json.load(f)
    else:
        historical_learnings = {}

    new_episode = {
        "messages": state["messages"],
        "status": "success" if state["successOccurred"] else "failure" if state["failureOccurred"] else "timed_out",
        "endReason": state["endReason"] if state["endReason"] != "" else "The game has run out of iterations."
    }

    llm = init_llm(
        provider=configurable.provider,
        model=configurable.model,
        temperature=configurable.temperature
    )

    failure_analysis_system_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(FAILURE_ANALYSIS_SYSTEM_PROMPT_TEMPLATE),
        HumanMessagePromptTemplate.from_template(
            template="""
            ## Historical Learnings: \n{historicalLearnings}\n
            ## New Episode: \n{newEpisode}\n
            """
        ),
    ])

    failure_analysis_agent = create_agent(
        llm=llm,
        prompt=failure_analysis_system_prompt,
        output_structure=HistoricalLearnings
    )

    result = failure_analysis_agent.invoke({
        "historicalLearnings": historical_learnings,
        "newEpisode": new_episode
    })

    with open(os.path.join(learning_path, "historical_learnings.json"), "w") as f:
        json.dump(result.model_dump(), f, indent=4)

    return {
        "messages": [
            {"learner": {**result.model_dump()}}
        ]
    }


def logger_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Log the final state and outcome of an agent episode to a JSON file.
    
    This node serves as the final logging step in the agent workflow, capturing
    the complete episode data including all messages, final status, and end reason.
    The log is saved to a file named with the thread ID for easy identification
    and retrieval.
    
    Args:
        state (AgentState): The current state of the agent containing all episode
                           information including messages, success/failure status,
                           and end reason.
        config (RunnableConfig): Configuration object containing logging settings
                                including log path and thread ID.
    
    Returns:
        dict: Empty dictionary as this is a terminal logging node that doesn't
              modify the state for further processing.
    """
    
    configurable = Configuration.from_runnable_config(config)
    log_path = configurable.log_path
    thread_id = configurable.thread_id

    os.makedirs(log_path, exist_ok=True)

    payload = {
        "messages": state["messages"],
        "status": "success" if state["successOccurred"] else "failure" if state["failureOccurred"] else "timed_out",
        "endReason": state["endReason"] if state["endReason"] != "" else "The game has run out of iterations."
    }

    with open(f"{log_path}/{thread_id}.json", "w") as f:
        json.dump(payload, f, indent=4)
    
    return {}
