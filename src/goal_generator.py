from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from .prompts import GOAL_GENERATOR_SYSTEM_PROMPT_TEMPLATE
from .structs import GoalGeneratorResponse
from .type import WorldState

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5).with_structured_output(GoalGeneratorResponse)

goal_generator_system_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=GOAL_GENERATOR_SYSTEM_PROMPT_TEMPLATE),
    # MessagesPlaceholder(variable_name="messages"),
    HumanMessage(content="## Current world state: \n{world_state}\n\n## Learnings from past failures: {learnings}")
])

chain = goal_generator_system_prompt | llm

def generate_goal(world_state: WorldState, learnings: str) -> GoalGeneratorResponse:
    return chain.invoke({"world_state": world_state, "learnings": learnings})

world_states = [WorldState(
    health=80,
    stamina=80,
    potionCount=2,
    treasureThreatLevel="high",
    enemyNearby=True,
    enemyLevel="very_high",
    isInSafeZone=False,
    isBackup=False
),

WorldState(
    health=20,
    stamina=5,
    potionCount=0,
    treasureThreatLevel="medium", 
    enemyNearby=True,
    enemyLevel="medium",
    isInSafeZone=False,
    isBackup=False
),

WorldState(
    health=85,
    stamina=15,
    potionCount=1,
    treasureThreatLevel="high",
    enemyNearby=True,
    enemyLevel="medium",
    isInSafeZone=False,
    isBackup=True
),


WorldState(
    health=70,
    stamina=2,
    potionCount=1,
    treasureThreatLevel="low",
    enemyNearby=False,
    enemyLevel=None,
    isInSafeZone=True,
    isBackup=False
),]



learnings = ''

if __name__ == "__main__":
    for world_state in world_states:
        response = generate_goal(world_state, learnings)
        with open("/Users/psykick/Documents/GitHub/dungeon-guardian/temp/generate goals.txt", "a") as f:
            f.write(f"World state: \n{world_state}\n")
            f.write(f"Response: \n{response}\n")
            f.write("\n")




