"""Общие фикстуры.

Тесты владеют своими сущностями: фикстура `created_entity` удаляет сущность
после теста. Это нужно, так как сервис не даёт изоляции (нет аренды/транзакций),
а прогон параллелится через pytest-xdist, и шаринг id между тестами был бы
источником гонок.

Слои: `core/` — транспорт/контракты/билдеры/ассерты. `positive/` и `negative/` —
сценарии. Маркеры задаются здесь, чтобы каждый тест-модуль не дублировал epic.
"""
from __future__ import annotations

from collections.abc import Iterator

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
        # Тест мог удалить сущность сам — teardown должен быть идемпотентным.
        pass
