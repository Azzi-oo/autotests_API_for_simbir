"""Интеграционные тесты CRUD эндпоинтов сервиса.

Каждый тест владеет созданными им сущностями: фикстура `created_entity` удаляет
сущность после теста, поэтому параллельный запуск (`pytest -n auto`) безопасен.
"""
from __future__ import annotations

import uuid

import allure
import pytest
import requests

from tests.api_client import ApiClient
from tests.models import (
    AdditionRequest,
    EntityListResponse,
    EntityRequest,
    EntityResponse,
)

pytestmark = [pytest.mark.api, allure.feature("Entity API")]


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _missing_id() -> int:
    # ID, которого заведомо нет в БД: случайное 9-значное число.
    return 900_000_000 + (uuid.uuid4().int % 99_999_999)


@allure.title("POST /api/create возвращает положительный идентификатор")
def test_create_returns_positive_id(api: ApiClient, sample_entity: EntityRequest) -> None:
    entity_id = api.create(sample_entity)
    try:
        assert entity_id > 0
    finally:
        api.delete(entity_id)


@allure.title("GET /api/get/{id} возвращает сущность с исходными полями")
def test_create_then_get_roundtrip(
    api: ApiClient, sample_entity: EntityRequest, created_entity: int
) -> None:
    fetched = api.get(created_entity)

    assert isinstance(fetched, EntityResponse)
    assert fetched.id == created_entity
    assert fetched.title == sample_entity.title
    assert fetched.verified == sample_entity.verified
    assert fetched.important_numbers == sample_entity.important_numbers
    assert fetched.addition.additional_info == sample_entity.addition.additional_info
    assert fetched.addition.additional_number == sample_entity.addition.additional_number
    assert fetched.addition.id > 0


@allure.title("PATCH /api/patch/{id} обновляет поля сущности")
def test_patch_updates_fields(api: ApiClient, created_entity: int) -> None:
    new_title = _unique("patched")
    updated = EntityRequest(
        title=new_title,
        verified=False,
        addition=AdditionRequest(
            additional_info=_unique("patched-info"),
            additional_number=777,
        ),
        important_numbers=[100, 200, 300],
    )

    api.patch(created_entity, updated)

    fetched = api.get(created_entity)
    assert fetched.title == new_title
    assert fetched.verified is False
    assert fetched.important_numbers == [100, 200, 300]
    assert fetched.addition.additional_info == updated.addition.additional_info
    assert fetched.addition.additional_number == 777


@allure.title("DELETE /api/delete/{id} действительно удаляет сущность")
def test_delete_removes_entity(api: ApiClient, sample_entity: EntityRequest) -> None:
    entity_id = api.create(sample_entity)
    api.delete(entity_id)

    with pytest.raises(requests.HTTPError):
        api.get(entity_id)


@allure.title("GET /api/getAll возвращает страницу, содержащую созданную сущность")
def test_get_all_contains_created_entity(
    api: ApiClient, sample_entity: EntityRequest, created_entity: int
) -> None:
    page = api.get_all(page=1, per_page=200)

    assert isinstance(page, EntityListResponse)
    assert page.page == 1
    assert page.perPage == 200
    assert any(item.id == created_entity for item in page.entity)


@allure.title("GET /api/getAll фильтрует по заголовку")
def test_get_all_filters_by_title(
    api: ApiClient, sample_entity: EntityRequest, created_entity: int
) -> None:
    page = api.get_all(title=sample_entity.title, page=1, per_page=50)

    assert [item.id for item in page.entity] == [created_entity]
    assert page.entity[0].title == sample_entity.title


@allure.title("GET /api/getAll фильтрует по признаку verified")
def test_get_all_filters_by_verified(
    api: ApiClient, sample_entity: EntityRequest, created_entity: int
) -> None:
    page = api.get_all(title=sample_entity.title, verified=True, page=1, per_page=50)

    assert any(item.id == created_entity for item in page.entity)
    assert all(item.verified is True for item in page.entity)


@allure.title("GET /api/getAll по несовпадающему заголовку возвращает пустой список")
def test_get_all_unknown_title_is_empty(api: ApiClient) -> None:
    page = api.get_all(title=_unique("no-such-title"), page=1, per_page=50)

    assert page.entity == []


@allure.title("GET /api/get/{id} для несуществующего id завершается ошибкой")
def test_get_missing_id_fails(api: ApiClient) -> None:
    with pytest.raises(requests.HTTPError):
        api.get(_missing_id())


@allure.title("DELETE /api/delete/{id} для несуществующего id завершается ошибкой")
def test_delete_missing_id_fails(api: ApiClient) -> None:
    with pytest.raises((AssertionError, requests.HTTPError)):
        api.delete(_missing_id())


@allure.title("PATCH /api/patch/{id} для несуществующего id завершается ошибкой")
def test_patch_missing_id_fails(api: ApiClient, sample_entity: EntityRequest) -> None:
    with pytest.raises((AssertionError, requests.HTTPError)):
        api.patch(_missing_id(), sample_entity)


@allure.title("Повторное удаление уже удалённой сущности завершается ошибкой")
def test_double_delete_fails(api: ApiClient, sample_entity: EntityRequest) -> None:
    entity_id = api.create(sample_entity)
    api.delete(entity_id)

    with pytest.raises((AssertionError, requests.HTTPError)):
        api.delete(entity_id)


@allure.title("Каждая операция Create возвращает уникальный идентификатор")
def test_create_ids_are_unique(api: ApiClient) -> None:
    ids: list[int] = []
    try:
        for _ in range(3):
            entity = EntityRequest(
                title=_unique("uniq"),
                verified=True,
                addition=AdditionRequest(
                    additional_info=_unique("info"),
                    additional_number=1,
                ),
                important_numbers=[1],
            )
            ids.append(api.create(entity))
        assert len(set(ids)) == len(ids)
    finally:
        for entity_id in ids:
            try:
                api.delete(entity_id)
            except Exception:
                pass
