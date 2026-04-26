"""Positive: GET /api/get/{id} и GET /api/getAll."""
from __future__ import annotations

from collections.abc import Callable

import allure
import pytest

from tests.core.api_client import ApiClient
from tests.core.assertions import assert_entity_matches_request
from tests.core.builders import entity_request
from tests.core.models import EntityListResponse, EntityRequest

pytestmark = [
    pytest.mark.api,
    pytest.mark.positive,
    allure.epic("Entity API"),
    allure.story("Read entity"),
]


@allure.title("GET /api/get/{id} возвращает сущность, созданную в POST")
@allure.severity(allure.severity_level.BLOCKER)
def test_get_returns_created_entity(
    api: ApiClient, new_entity: EntityRequest, created_entity: int
) -> None:
    fetched = api.get(created_entity)
    assert fetched.id == created_entity
    assert_entity_matches_request(new_entity, fetched)


@allure.title("GET /api/getAll возвращает страницу, содержащую созданную сущность")
@allure.severity(allure.severity_level.CRITICAL)
def test_list_contains_created_entity(api: ApiClient, created_entity: int) -> None:
    page = api.get_all(page=1, per_page=200)
    assert isinstance(page, EntityListResponse)
    assert page.page == 1
    assert page.perPage == 200
    assert any(item.id == created_entity for item in page.entity)


@allure.title("Фильтр по уникальному title возвращает ровно одну запись")
@allure.severity(allure.severity_level.CRITICAL)
def test_list_filter_by_title_returns_single_match(
    api: ApiClient, new_entity: EntityRequest, created_entity: int
) -> None:
    page = api.get_all(title=new_entity.title, page=1, per_page=50)
    assert [item.id for item in page.entity] == [created_entity]


@allure.title("Фильтр по verified возвращает только сущности с заданным флагом")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize("verified", [True, False])
def test_list_filter_by_verified(
    api: ApiClient, make_entity: Callable[..., int], verified: bool
) -> None:
    payload = entity_request(verified=verified)
    entity_id = make_entity(payload)
    page = api.get_all(title=payload.title, verified=verified, page=1, per_page=50)
    assert any(item.id == entity_id for item in page.entity)
    assert all(item.verified is verified for item in page.entity)


@allure.title("Пагинация: per_page ограничивает размер страницы")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize("per_page", [1, 5, 25])
def test_list_respects_per_page(api: ApiClient, per_page: int) -> None:
    page = api.get_all(page=1, per_page=per_page)
    assert page.perPage == per_page
    assert len(page.entity) <= per_page
