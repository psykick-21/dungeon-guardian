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
    PLANNER_SYSTEM_PROMPT_TEMPLATE
)
from .type import Goals, Goal
from .structs import (
    GoalGeneratorResponse,
    PlannerResponse
)
import time
import os
from .action import actions, actions_dict
import json



def goal_generator_node(state: AgentState, config: RunnableConfig) -> AgentState:
    
    configurable = Configuration.from_runnable_config(config)
    
    llm = init_llm(
        provider=configurable.provider,
        model=configurable.model,
        temperature=configurable.temperature
    )

    goal_generator_system_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(GOAL_GENERATOR_SYSTEM_PROMPT_TEMPLATE),
        MessagesPlaceholder(variable_name="messages"),
        HumanMessagePromptTemplate.from_template(
            template = """
            ## Current world state: \n{current_world_state}\n
            ## Learnings from past failures: ''
            """
        )
    ])

    goal_generator_agent = create_agent(
        llm=llm,
        prompt=goal_generator_system_prompt,
        output_structure=GoalGeneratorResponse
    )

    result = goal_generator_agent.invoke(state)

    return {
        "messages": [
            HumanMessage(content=f"Current world state: \n{state['current_world_state']}"),
            AIMessage(content=f"{result}")
        ],
        "goals": Goals(primaryGoal=result.primaryGoal, secondaryGoal=result.secondaryGoal),
        "suggestions": result.adaptationSuggestions,
        "goal_justification": result.justification
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
            ## Current world state:\n{current_world_state}\n
            ## Goals: \n{goals}\n
            ## Suggestions: \n{suggestions}\n
            """
        )
    ])

    planner_agent = create_agent(
        llm=llm,
        prompt=planner_system_prompt,
        output_structure=PlannerResponse
    )

    result = planner_agent.invoke({**state, "actions": actions, "goals": Goal._member_names_})

    return {
        "messages": [AIMessage(content=f"{result}")],
        "action_sequence": result.actionSequence,
        "planner_justification": result.reasoning
    }



def action_executor_node(state: AgentState, config: RunnableConfig) -> AgentState:
    
    previous_world_state = state["current_world_state"]
    current_world_state = state["current_world_state"].copy()
    action_sequence = state["action_sequence"]
    
    executed_actions = []
    failure_occurred = False
    failure_reason = ""
    action_failed = False

    game_message = ""

    for action_name in action_sequence:
        
        action_obj = actions_dict[action_name]
        preconditions_met = True
        
        # Check all preconditions
        for precondition in action_obj.preconditions:
            if not eval(precondition)(current_world_state):
                preconditions_met = False
                game_message += f"Action {action_name} failed because {precondition} is not met.\n"
                action_failed = True
                break

        if preconditions_met:
            # Execute the action by applying its effects
            for key, value in eval(action_obj.effects).items():
                current_world_state[key] = value(current_world_state)
            
            executed_actions.append(action_name)
            
            # Check for failure conditions after each action
            is_failed, reason = check_failure_conditions(current_world_state)
            if is_failed:
                failure_occurred = True
                failure_reason = reason
                game_message += f"You have failed due to the following reason: {reason}.\nPlease try again."

                return {
                    "messages": [
                        SystemMessage(content=game_message)
                    ],
                    "current_world_state": previous_world_state,
                    "previous_world_state": previous_world_state,
                    "failure_occurred": failure_occurred,
                    "failure_reason": failure_reason,
                    "action_failed": action_failed,
                }
                
        else:
            # Action cannot be executed due to unmet preconditions
            continue

    game_message += f"No game failure occurred."


    return {
        "messages": [
            SystemMessage(content=game_message)
        ],
        "current_world_state": current_world_state,
        "previous_world_state": previous_world_state,
        "failure_occurred": failure_occurred,
        "failure_reason": failure_reason,
        "action_failed": action_failed,
    }
    


def check_success_conditions_node(state: AgentState, config: RunnableConfig) -> AgentState:
    
    game_message = ""
    is_successful, success_msg = check_success_conditions(state['current_world_state'])
    if is_successful:
        game_message += f"Congratulations! {success_msg}\n"
        
        return {
            "messages": [
                SystemMessage(content=game_message)
            ],
            "success_occurred": is_successful,
            "success_reason": success_msg
        }
    
    else:
        game_message += f"The game is still running.\n"
        return {
            "messages": [
                SystemMessage(content=game_message)
            ],
            "success_occurred": is_successful,
            "success_reason": success_msg
        }
    

def logger_node(state: AgentState, config: RunnableConfig) -> AgentState:
    
    configurable = Configuration.from_runnable_config(config)
    log_path = configurable.log_path
    thread_id = configurable.thread_id

    payload = {
        "thread_id": thread_id,
        "messages": dumps(state["messages"]),
        "status": "success" if state["success_occurred"] else "failure",
        "success_reason": state["success_reason"],
    }

    with open(f"{log_path}/{thread_id}.json", "w") as f:
        f.write(json.dumps(payload))
    
    return {}