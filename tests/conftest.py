"""Общие фикстуры.

Сервис не имеет функций управления арендой/очистки, и тесты выполняются параллельно
с pytest-xdist, поэтому каждый тест владеет созданными им сущностями и удаляет их
при завершении работы. Ни один тест не зависит от идентификаторов, созданных другим тестом.
"""
from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest
import requests

from tests.api_client import ApiClient
from tests.models import AdditionRequest, EntityRequest


@pytest.fixture(scope="session")
def api() -> ApiClient:
    client = ApiClient()
    try:
        requests.get(f"{client.base_url}/api/getAll", timeout=5).raise_for_status()
    except Exception as exc:
        pytest.fail(f"service unreachable at {client.base_url}: {exc}")
    return client


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


@pytest.fixture
def sample_entity() -> EntityRequest:
    return EntityRequest(
        title=_unique("title"),
        verified=True,
        addition=AdditionRequest(
            additional_info=_unique("info"),
            additional_number=42,
        ),
        important_numbers=[1, 2, 3, 5, 8, 13],
    )


@pytest.fixture
def created_entity(api: ApiClient, sample_entity: EntityRequest) -> Iterator[int]:
    entity_id = api.create(sample_entity)
    yield entity_id
    try:
        api.delete(entity_id)
    except Exception:
        pass
