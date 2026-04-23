"""Pydantic-модели — контракт ответов API.

Все данные ответов в тестах десериализуются этими моделями.
`extra="forbid"` защищает от тихой потери новых полей: если сервис добавит
поле, десериализация упадёт, и мы обновим модель осознанно.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AdditionRequest(_Strict):
    additional_info: str
    additional_number: int


class EntityRequest(_Strict):
    title: str
    verified: bool
    addition: AdditionRequest
    important_numbers: list[int]


class AdditionResponse(_Strict):
    id: int
    additional_info: str
    additional_number: int


class EntityResponse(_Strict):
    id: int
    title: str
    verified: bool
    addition: AdditionResponse
    important_numbers: list[int]


class EntityListResponse(_Strict):
    """Реальная форма GET /api/getAll.

    Swagger обещает голый массив, но сервис оборачивает ответ в объект
    с пагинацией. Тесты сверяются с фактическим поведением.
    """

    entity: list[EntityResponse] = Field(default_factory=list)
    page: int
    perPage: int
