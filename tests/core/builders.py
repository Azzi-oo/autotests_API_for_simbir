"""Фабрики тестовых данных.

Принцип: тест не должен ни хардкодить «магические» значения, ни заботиться
о генерации уникальности. Каждая фабрика возвращает валидный объект
с разумными случайными дефолтами; любое поле переопределяется kwargs'ами
(паттерн Test Data Builder / Object Mother).

Пример:

    entity_request()                        # полностью случайная сущность
    entity_request(verified=True)           # переопределён только verified
    entity_request(title="fixed-title")     # фиксированный заголовок

Подход соответствует рекомендациям pytest-сообщества и идиомам xUnit
(см. "xUnit Test Patterns", M. Meszaros, главы Object Mother / Test Data Builder).
"""
from __future__ import annotations

import random
import string
import uuid
from typing import Any

from tests.core.models import AdditionRequest, EntityRequest


def random_slug(prefix: str, *, length: int = 12) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:length]}"


def random_sentence(words: int = 3) -> str:
    return " ".join(
        "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
        for _ in range(words)
    )


def random_int(low: int = 1, high: int = 10_000) -> int:
    return random.randint(low, high)


def random_numbers(count: int | None = None) -> list[int]:
    n = count if count is not None else random.randint(1, 8)
    return [random.randint(-1000, 1000) for _ in range(n)]


def addition_request(**overrides: Any) -> AdditionRequest:
    payload: dict[str, Any] = {
        "additional_info": random_sentence(),
        "additional_number": random_int(),
    }
    payload.update(overrides)
    return AdditionRequest(**payload)


def entity_request(**overrides: Any) -> EntityRequest:
    """Валидная случайная сущность. Передайте kwargs для фиксации полей."""
    payload: dict[str, Any] = {
        "title": random_slug("title"),
        "verified": random.choice([True, False]),
        "addition": addition_request(),
        "important_numbers": random_numbers(),
    }
    payload.update(overrides)
    return EntityRequest(**payload)


def missing_entity_id() -> int:
    """Идентификатор, заведомо отсутствующий в БД.

    Берём из верхнего диапазона int32, чтобы не конфликтовать с реальными
    автоинкрементными id даже при долгой эксплуатации сервиса.
    """
    return random.randint(900_000_000, 999_999_999)
