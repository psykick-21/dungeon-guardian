from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import (
    ChatPromptTemplate, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate, 
    MessagesPlaceholder
)
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.load import dumps, loads
from langgraph.types import Command, Send
from langgraph.graph import END
from typing import Literal, Dict
from .states import AgentState
from .configuration import Configuration
from .utils import init_llm, create_agent, check_failure_conditions, check_success_conditions
from .prompts import (
    GOAL_GENERATOR_SYSTEM_PROMPT_TEMPLATE,
    PLANNER_SYSTEM_PROMPT_TEMPLATE,
    FAILURE_ANALYSIS_SYSTEM_PROMPT_TEMPLATE
)
from .type import Goals, Goal
from .structs import (
    GoalGeneratorResponse,
    PlannerResponse
)
import time
import os
from .action import action_descriptions, actions_dict
import json



def goal_generator_node(state: AgentState, config: RunnableConfig) -> AgentState:
    
    configurable = Configuration.from_runnable_config(config)
    learning_path = configurable.learning_path

    if os.path.exists(os.path.join(learning_path, "failure_analysis.txt")):
        with open(os.path.join(learning_path, "failure_analysis.txt"), "r") as f:
            failure_analysis = f.read()
    else:
        failure_analysis = ""

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
            ## Learnings from past failures: \n{failureAnalysis}\n
            """
        )
    ])

    goal_generator_agent = create_agent(
        llm=llm,
        prompt=goal_generator_system_prompt,
        output_structure=GoalGeneratorResponse
    )

    result = goal_generator_agent.invoke({**state, "failureAnalysis": failure_analysis})

    return {
        "messages": [
            {"worldState": state["currentWorldState"]},
            {**result.model_dump()}
        ],
        "currentWorldState": state["currentWorldState"],
        **result.model_dump()
    }



def planner_node(state: AgentState, config: RunnableConfig) -> AgentState:
    
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
        "messages": [{**result.model_dump()}],
        **result.model_dump()
    }



def action_executor_node(state: AgentState, config: RunnableConfig) -> AgentState:
    
    previous_world_state = state["currentWorldState"]
    current_world_state = state["currentWorldState"].copy()
    action_sequence = state["actionSequence"]
    
    executed_actions = []
    failure_occurred = False
    failure_reason = ""
    action_failed = False

    game_message = ""

    for action_name in action_sequence:
        
        action_obj = actions_dict[action_name]
        preconditions_met = True
        
        # Check all preconditions
        for precondition in action_obj["preconditions"]:
            if not precondition(current_world_state):
                preconditions_met = False
                game_message += f"Action {action_name} failed because precondition is not met.\n"
                action_failed = True
                break

        if preconditions_met:
            # Execute the action by applying its effects
            for key, value in action_obj["effects"].items():
                current_world_state[key] = value(current_world_state)
            
            executed_actions.append(action_name)
            
            # Check for failure conditions after each action
            is_failed, reason = check_failure_conditions(current_world_state)
            if is_failed:
                failure_occurred = True
                failure_reason = reason
                game_message += f"You have failed due to the following reason: {reason}.\nPlease try again."
                game_message += f"Executed actions: {executed_actions}"

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
            # Action cannot be executed due to unmet preconditions
            continue

    game_message += f"No game failure occurred."
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

    configurable = Configuration.from_runnable_config(config)
    iterations = state.get("iterations", 0) + 1
    
    game_message = ""
    is_successful, success_msg = check_success_conditions(state['currentWorldState'])
    
    if is_successful:
        game_message += f"Congratulations! {success_msg}\n"
        
        return {
            "messages": [
                {"gameMessage": game_message}
            ],
            "successOccurred": is_successful,
            "endReason": success_msg
        }
    
    else:
    
        if iterations >= configurable.total_iterations:
            return {
                "messages": [
                    {"gameMessage": "You have run out of maximum permissible iterations. The game has ended without success or failure."}
                ],
                "successOccurred": is_successful,
                "endReason": "The game has run out of iterations."
            }
        
        game_message += f"The game is still running. Please continue.\n"
        return {
            "messages": [
                {"gameMessage": game_message}
            ],
            "successOccurred": is_successful,
            "endReason": success_msg
        }
    

def logger_node(state: AgentState, config: RunnableConfig) -> AgentState:
    
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



def failure_analysis_node(state: AgentState, config: RunnableConfig) -> AgentState:
    
    configurable = Configuration.from_runnable_config(config)
    learning_path = configurable.learning_path

    os.makedirs(learning_path, exist_ok=True)

    if os.path.exists(os.path.join(learning_path, "failure_analysis.txt")):
        with open(os.path.join(learning_path, "failure_analysis.txt"), "r") as f:
            failure_analysis = f.read()
    else:
        failure_analysis = ""

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
            ## Historical Failure Summary:
            \nThis is what you have analyzed and created in the past. Use this and the content from new episode to create a new failure analysis.\n
            {failure_analysis}

            ## New Episode:
            {new_episode}
            """
        ),
    ])

    failure_analysis_agent = create_agent(
        llm=llm,
        prompt=failure_analysis_system_prompt,
    )

    result = failure_analysis_agent.invoke({
        "failure_analysis": failure_analysis,
        "new_episode": new_episode
    })

    with open(os.path.join(learning_path, "failure_analysis.txt"), "w") as f:
        f.write(result.content)

    return {
        "messages": [
            {"learnerMessage": result.content}
        ]
    }
