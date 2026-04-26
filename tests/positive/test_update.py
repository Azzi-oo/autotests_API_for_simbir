"""Positive: PATCH /api/patch/{id}."""
from __future__ import annotations

from collections.abc import Callable

import allure
import pytest

from tests.core.api_client import ApiClient
from tests.core.assertions import assert_entity_matches_request
from tests.core.builders import entity_request

pytestmark = [
    pytest.mark.api,
    pytest.mark.positive,
    allure.epic("Entity API"),
    allure.story("Update entity"),
]


@allure.title("PATCH перезаписывает все поля сущности")
@allure.severity(allure.severity_level.BLOCKER)
def test_patch_replaces_all_fields(api: ApiClient, created_entity: int) -> None:
    replacement = entity_request()
    api.patch(created_entity, replacement)

    fetched = api.get(created_entity)
    assert_entity_matches_request(replacement, fetched)


@allure.title("Серия PATCH применяет последнее значение")
@allure.severity(allure.severity_level.NORMAL)
def test_successive_patches_keep_last_value(api: ApiClient, created_entity: int) -> None:
    first = entity_request()
    last = entity_request()

    api.patch(created_entity, first)
    api.patch(created_entity, last)

    fetched = api.get(created_entity)
    assert_entity_matches_request(last, fetched)


@allure.title("PATCH обновляет только целевую сущность, не затрагивая соседние")
@allure.severity(allure.severity_level.CRITICAL)
def test_patch_isolated_to_target(api: ApiClient, make_entity: Callable[..., int]) -> None:
    second_payload = entity_request()
    first_id = make_entity()
    second_id = make_entity(second_payload)

    api.patch(first_id, entity_request())

    fetched_second = api.get(second_id)
    assert_entity_matches_request(second_payload, fetched_second)
