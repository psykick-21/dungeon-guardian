from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import (
    ChatPromptTemplate, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate, 
    MessagesPlaceholder
)
from langchain_core.messages import HumanMessage
from langgraph.types import Command, Send
from typing import Literal, Dict
from .states import AgentState
from .configuration import Configuration
from .utils import init_llm, create_agent
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



def goal_generator_node(state: AgentState, config: RunnableConfig) -> AgentState:
    
    configurable = Configuration.from_runnable_config(config)
    
    llm = init_llm(
        provider=configurable.provider,
        model=configurable.model,
        temperature=configurable.temperature
    )

    goal_generator_system_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(GOAL_GENERATOR_SYSTEM_PROMPT_TEMPLATE),
        HumanMessagePromptTemplate.from_template("## Current world state: \n{current_world_state}\n\n## Learnings from past failures: ''")
    ])

    goal_generator_agent = create_agent(
        llm=llm,
        prompt=goal_generator_system_prompt,
        output_structure=GoalGeneratorResponse
    )

    result = goal_generator_agent.invoke(state)

    with open("/Users/psykick/Documents/GitHub/dungeon-guardian/temp/goal_generator_response.json", "w") as f:
        f.write(result.model_dump_json())

    return {
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

    with open("/Users/psykick/Documents/GitHub/dungeon-guardian/temp/planner_response.json", "w") as f:
        f.write(result.model_dump_json())

    return {
        "action_sequence": result.actionSequence,
        "planner_justification": result.reasoning
    }



def action_executor_node(state: AgentState, config: RunnableConfig) -> AgentState:
    
    previous_world_state = state["current_world_state"]
    current_world_state = state["current_world_state"].copy(deep=True)
    action_sequence = state["action_sequence"]

    for action in action_sequence:
        action_obj = actions_dict[action]
        for precondition in action_obj.preconditions:
            if not eval(precondition)(current_world_state):
                break
        else:
            action_obj.execute(current_world_state)

    
    pass
    