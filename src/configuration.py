from dataclasses import dataclass, fields
from langchain_core.runnables import RunnableConfig
import os
from typing import Any
import uuid

@dataclass(kw_only=True)
class Configuration:

    provider: str = "openai"
    model: str = "gpt-4o-mini"
    temperature: float = 0.5
    log_path: str = "/Users/psykick/Documents/GitHub/dungeon-guardian/temp/game_logs"
    learning_path: str = "/Users/psykick/Documents/GitHub/dungeon-guardian/temp/learning"
    thread_id: str = str(uuid.uuid4())
    
    @classmethod
    def from_runnable_config(
        cls,
        config: RunnableConfig
    ) -> "Configuration":
        
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name, f.default))
            for f in fields(cls)
            if f.init
        }

        return cls(**values)