"""Pydantic models это зеркало сервиса DTOs из docs/swagger.yaml.

Все данные ответов, полученные в тестах, ДОЛЖНЫ быть десериализованы с помощью
этих моделей. `model_config = ConfigDict(extra="forbid")` предотвращает отклонения:
если сервис добавляет поле, которое мы не знаем, десериализация завершается с ошибкой, а не незаметно теряет данные.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AdditionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    additional_info: str
    additional_number: int


class EntityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    verified: bool
    addition: AdditionRequest
    important_numbers: list[int]


class AdditionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    additional_info: str
    additional_number: int


class EntityResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    title: str
    verified: bool
    addition: AdditionResponse
    important_numbers: list[int]


class EntityListResponse(BaseModel):
    """Наблюдаемая форма из GET /api/getAll.

    Примечание: Swagger рекламирует простой массив, но работающий сервис его оборачивает.
    Тесты проверяют соответствие реальной форме, а не спецификации.
    """

    model_config = ConfigDict(extra="forbid")

    entity: list[EntityResponse] = Field(default_factory=list)
    page: int
    perPage: int
