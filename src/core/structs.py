from pydantic import BaseModel, Field


class GoalGeneratorResponse(BaseModel):
    primaryGoal: str = Field(description="The primary goal of the guardian")
    secondaryGoal: str = Field(description="The secondary goal of the guardian")
    justification: str = Field(description="The justification for the goal selection")
    adaptationSuggestions: str | None = Field(default=None, description="The suggestions for improvement in actions based on historical patterns. If no failures occurred due to actions, this should be None")

