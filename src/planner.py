from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from .prompts import PLANNER_SYSTEM_PROMPT_TEMPLATE
from .structs import PlannerResponse
from .type import WorldState

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5).with_structured_output(PlannerResponse)

planner_system_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=PLANNER_SYSTEM_PROMPT_TEMPLATE),
    # MessagesPlaceholder(variable_name="messages"),
    HumanMessage(content="{input}")
])

chain = planner_system_prompt | llm

def generate_plan(world_state: WorldState, primary_goal: str, secondary_goal: str) -> PlannerResponse:
    return chain.invoke({
        "input": {
            "world_state": world_state,
            "primary_goal": primary_goal,
            "secondary_goal": secondary_goal
        }
    })


inputs = [
    {
        "world_state": WorldState(
            health=80,
            stamina=80,
            potionCount=2,
            treasureThreatLevel="high",
            enemyNearby=True,
            enemyLevel="very_high",
            isInSafeZone=False,
            isBackup=False
        ),
        "primary_goal": "EliminateThreat",
        "secondary_goal": "ProtectTreasure"
    },
    {
        "world_state": WorldState(
            health=20,
            stamina=5,
            potionCount=0,
            treasureThreatLevel="medium",
            enemyNearby=True,
            enemyLevel="medium",
            isInSafeZone=False,
            isBackup=False
        ),
        "primary_goal": "Survive",
        "secondary_goal": "PrepareForBattle"
    },
    {
        "world_state": WorldState(
            health=85,
            stamina=15,
            potionCount=1,
            treasureThreatLevel="high",
            enemyNearby=True,
            enemyLevel="medium",
            isInSafeZone=False,
            isBackup=True
        ),
        "primary_goal": "Survive",
        "secondary_goal": "PrepareForBattle"
    },
    {
        "world_state": WorldState(
            health=70,
            stamina=2,
            potionCount=1,
            treasureThreatLevel="low",
            enemyNearby=False,
            enemyLevel=None,
            isInSafeZone=True,
            isBackup=False
        ),
        "primary_goal": "EliminateThreat",
        "secondary_goal": "ProtectTreasure"
    }
]



if __name__ == "__main__":
    for i in inputs:
        response = generate_plan(**i)
        with open("/Users/psykick/Documents/GitHub/dungeon-guardian/temp/planner.txt", "a") as f:
            f.write(f"Input: \n{i}\n")
            f.write(f"Response: \n{response}\n")
            f.write("\n")




