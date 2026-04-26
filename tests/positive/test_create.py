"""Positive: POST /api/create."""
from __future__ import annotations

from collections.abc import Callable

import allure
import pytest

from tests.core.api_client import ApiClient
from tests.core.assertions import assert_entity_matches_request
from tests.core.models import EntityRequest

pytestmark = [
    pytest.mark.api,
    pytest.mark.positive,
    allure.epic("Entity API"),
    allure.story("Create entity"),
]


@allure.title("Создание сущности возвращает положительный id")
@allure.severity(allure.severity_level.BLOCKER)
def test_create_returns_positive_id(created_entity: int) -> None:
    assert created_entity > 0


@allure.title("Создание нескольких сущностей возвращает уникальные идентификаторы")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("count", [2, 5])
def test_create_returns_unique_ids(make_entity: Callable[..., int], count: int) -> None:
    ids = [make_entity() for _ in range(count)]
    assert len(set(ids)) == count, f"expected unique ids, got duplicates in {ids}"


@allure.title("Поля созданной сущности совпадают с отправленным запросом")
@allure.severity(allure.severity_level.BLOCKER)
def test_created_entity_matches_request(
    api: ApiClient, new_entity: EntityRequest, created_entity: int
) -> None:
    fetched = api.get(created_entity)
    assert fetched.id == created_entity
    assert fetched.addition.id > 0
    assert_entity_matches_request(new_entity, fetched)


@allure.title("Сервис сохраняет массив important_numbers ровно как отправленный")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize(
    "numbers",
    [
        [0],
        [-1, 0, 1],
        [1_000_000, -1_000_000],
        list(range(20)),
    ],
    ids=["single-zero", "around-zero", "extremes", "twenty-asc"],
)
def test_create_preserves_important_numbers(
    api: ApiClient, make_entity: Callable[..., int], numbers: list[int]
) -> None:
    entity_id = make_entity(important_numbers=numbers)
    fetched = api.get(entity_id)
    assert fetched.important_numbers == numbers


@allure.title("Сервис сохраняет значение verified как отправленное")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize("verified", [True, False])
def test_create_preserves_verified_flag(
    api: ApiClient, make_entity: Callable[..., int], verified: bool
) -> None:
    entity_id = make_entity(verified=verified)
    fetched = api.get(entity_id)
    assert fetched.verified is verified
