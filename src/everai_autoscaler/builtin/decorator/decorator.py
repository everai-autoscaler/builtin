from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict, List


class Decorator(BaseModel):
    name: str
    arguments: Dict[str, str] = Field(default={})

    @staticmethod
    def from_json(data) -> Decorator:
        return Decorator.model_validate_json(data)


class Decorators(BaseModel):
    arguments: List[Decorators] = Field(default=[])
    factors: List[Decorators] = Field(default=[])

    @staticmethod
    def from_json(data) -> Decorators:
        return Decorators.model_validate_json(data)
