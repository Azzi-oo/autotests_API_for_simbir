"""Positive: DELETE /api/delete/{id}."""
from __future__ import annotations

import allure
import pytest
import requests

from tests.core.api_client import ApiClient
from tests.core.builders import entity_request

pytestmark = [
    pytest.mark.api,
    pytest.mark.positive,
    allure.epic("Entity API"),
    allure.story("Delete entity"),
]


@allure.title("После DELETE сущность недоступна для чтения по id")
@allure.severity(allure.severity_level.BLOCKER)
def test_deleted_entity_is_not_readable(api: ApiClient) -> None:
    entity_id = api.create(entity_request())
    api.delete(entity_id)

    with pytest.raises(requests.HTTPError):
        api.get(entity_id)


@allure.title("После DELETE сущность исчезает из списка getAll")
@allure.severity(allure.severity_level.CRITICAL)
def test_deleted_entity_is_absent_from_list(api: ApiClient) -> None:
    payload = entity_request()
    entity_id = api.create(payload)
    api.delete(entity_id)

    page = api.get_all(title=payload.title, page=1, per_page=50)
    assert all(item.id != entity_id for item in page.entity)
