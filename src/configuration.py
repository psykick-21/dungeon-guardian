from dataclasses import dataclass, fields
from langchain_core.runnables import RunnableConfig
import os
from typing import Any

@dataclass(kw_only=True)
class Configuration:

    provider: str = "openai"
    model: str = "gpt-4o-mini"
    temperature: float = 0.5
    
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