from pydantic import BaseModel, Field


class GoalGeneratorResponse(BaseModel):
    primaryGoal: str = Field(description="The primary goal of the guardian")
    secondaryGoal: str = Field(description="The secondary goal of the guardian")
    goalJustification: str = Field(description="The justification for the goal selection")
    actionFailureSuggestions: str | None = Field(default=None, description="The reasons for the action failures in previous attempts. If no failures occurred due to actions, this should be None")


class PlannerResponse(BaseModel):
    actionSequence: list[str] = Field(description="A sequence of permitted actions to achieve the primary goal, with fallback for the secondary goal.")
    plannerJustification: str = Field(description="The reasoning for the action sequence")

