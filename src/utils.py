from typing import Literal, List, Union
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from .type import WorldState

load_dotenv()




def init_llm(
        provider: Literal["openai", "anthropic", "google", "ollama"],
        model: str,
        temperature: float = 0.5,
):
    """
    Initialize and return a language model chat interface based on the specified provider.

    This function creates a chat interface for different LLM providers including OpenAI, 
    Anthropic, Google, and Ollama. It handles API key validation and configuration for
    each provider.

    Args:
        provider: The LLM provider to use. Must be one of "openai", "anthropic", "google", or "ollama".
        model: The specific model name/identifier to use with the chosen provider.
        temperature: Controls randomness in the model's output. Higher values (e.g. 0.8) make the output
                    more random, while lower values (e.g. 0.2) make it more deterministic. Defaults to 0.5.

    Returns:
        A configured chat interface for the specified provider and model.

    Raises:
        ValueError: If the required API key environment variable is not set for the chosen provider
                   (except for Ollama which runs locally).
    """
    if provider == "openai":
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OPENAI_API_KEY is not set. Please set it in your environment variables.")
        return ChatOpenAI(model=model, temperature=temperature, api_key=os.environ["OPENAI_API_KEY"])
    elif provider == "anthropic":
        if "ANTHROPIC_API_KEY" not in os.environ:
            raise ValueError("ANTHROPIC_API_KEY is not set. Please set it in your environment variables.")
        return ChatAnthropic(model=model, temperature=temperature, api_key=os.environ["ANTHROPIC_API_KEY"])
    elif provider == "google":
        if "GOOGLE_API_KEY" not in os.environ:
            raise ValueError("GOOGLE_API_KEY is not set. Please set it in your environment variables.")
        return ChatGoogleGenerativeAI(model=model, temperature=temperature, api_key=os.environ["GOOGLE_API_KEY"])
    elif provider == "ollama":
        return ChatOllama(model=model, temperature=temperature)
    


def create_agent(
        llm: Union[ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI, ChatOllama],
        prompt: ChatPromptTemplate,
        output_structure: BaseModel = None,
        tools: List[BaseModel] = None,
):
    """
    Create and configure a language model agent with optional structured output and tools.

    This function creates an agent by combining a language model with a prompt template,
    and optionally adds structured output validation and tools.

    Args:
        llm: The language model to use. Can be OpenAI, Anthropic, Google, or Ollama chat model.
        prompt: The prompt template that defines the agent's behavior and instructions.
        output_structure: Optional Pydantic model to validate and structure the agent's output.
        tools: Optional list of tools/functions that the agent can use.

    Returns:
        A configured agent that combines the language model, prompt, and optional components.
    """
    
    if output_structure:
        llm = llm.with_structured_output(output_structure)
    
    agent = prompt | llm

    if tools:
        agent = agent.with_tools(tools)

    return agent

def check_failure_conditions(world_state: WorldState) -> tuple[bool, str]:
    """
    Check if the agent has failed based on the current world state.
    
    Args:
        world_state: The current WorldState to check
        
    Returns:
        tuple[bool, str]: (is_failed, failure_reason)
            - is_failed: True if the agent has failed, False otherwise
            - failure_reason: Description of why the agent failed, empty string if not failed
    """
    
    if world_state.get('health', 100) <= 0:
        return True, "Agent died - health reached 0"
    
    if world_state.get('treasureHealth', 100) <= 0:
        return True, "Treasure was destroyed - treasureHealth reached 0"
    
    if world_state.get('stamina', 100) <= 0:
        return True, "Agent is exhausted - stamina reached 0"
    
    return False, ""


def check_success_conditions(world_state: WorldState) -> tuple[bool, str]:
    """
    Check if the agent has succeeded based on the current world state.
    
    Args:
        world_state: The current WorldState to check
        
    Returns:
        tuple[bool, str]: (is_successful, success_reason)
            - is_successful: True if the agent has succeeded, False otherwise
            - success_reason: Description of why the agent succeeded, empty string if not successful
    """
    
    # Primary success condition: All threats eliminated and treasure protected
    if (world_state.get('enemyNearby', True) == False and
        world_state.get('treasureThreatLevel', 'high') == 'low'):
        return True, "Mission accomplished! All enemies defeated, treasure threat neutralized, and treasure well-protected"
    
    return False, ""
