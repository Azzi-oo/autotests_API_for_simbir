"""Общие фикстуры.

Тесты владеют своими сущностями: фикстуры `created_entity` и `make_entity`
удаляют созданное в teardown. Это нужно, так как сервис не даёт изоляции
(нет аренды/транзакций), а прогон параллелится через pytest-xdist, и шаринг
id между тестами был бы источником гонок.

Слои: `core/` — транспорт/контракты/билдеры/ассерты. `positive/` и `negative/` —
сценарии. Маркеры задаются здесь, чтобы каждый тест-модуль не дублировал epic.
"""
from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

import pytest
import requests

from tests.core.api_client import ApiClient
from tests.core.builders import entity_request
from tests.core.models import EntityRequest


@pytest.fixture(scope="session")
def api() -> ApiClient:
    client = ApiClient()
    try:
        requests.get(f"{client.base_url}/api/getAll", timeout=5).raise_for_status()
    except Exception as exc:
        pytest.fail(f"service unreachable at {client.base_url}: {exc}")
    return client


@pytest.fixture
def new_entity() -> EntityRequest:
    """Свежий валидный payload для POST /api/create."""
    return entity_request()


@pytest.fixture
def created_entity(api: ApiClient, new_entity: EntityRequest) -> Iterator[int]:
    """Создаёт сущность, возвращает её id и убирает её в teardown."""
    entity_id = api.create(new_entity)
    yield entity_id
    try:
        api.delete(entity_id)
    except Exception:
        pass


@pytest.fixture
def make_entity(api: ApiClient) -> Iterator[Callable[..., int]]:
    """Фабрика сущностей с автоматической очисткой.

    Принимает готовый ``EntityRequest`` или kwargs, форвардящиеся в
    ``entity_request()``. Все созданные id удаляются в teardown в обратном
    порядке создания, ошибки удаления глушатся (тест мог их уже удалить сам).
    """
    created_ids: list[int] = []

    def _create(payload: EntityRequest | None = None, **overrides: Any) -> int:
        if payload is None:
            payload = entity_request(**overrides)
        elif overrides:
            raise TypeError("pass either a payload or kwargs, not both")
        entity_id = api.create(payload)
        created_ids.append(entity_id)
        return entity_id

    yield _create

    for entity_id in reversed(created_ids):
        try:
            api.delete(entity_id)
        except Exception:
            pass
