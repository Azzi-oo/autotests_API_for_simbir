"""Negative: операции над несуществующим id."""
from __future__ import annotations

import allure
import pytest
import requests

from tests.core.api_client import ApiClient
from tests.core.builders import entity_request, missing_entity_id

pytestmark = [
    pytest.mark.api,
    pytest.mark.negative,
    allure.epic("Entity API"),
    allure.story("Not found"),
]


@allure.title("GET по несуществующему id возвращает ошибку")
@allure.severity(allure.severity_level.NORMAL)
def test_get_missing_id_fails(api: ApiClient) -> None:
    with pytest.raises(requests.HTTPError):
        api.get(missing_entity_id())


@allure.title("DELETE по несуществующему id возвращает ошибку")
@allure.severity(allure.severity_level.NORMAL)
def test_delete_missing_id_fails(api: ApiClient) -> None:
    with pytest.raises((AssertionError, requests.HTTPError)):
        api.delete(missing_entity_id())


@allure.title("PATCH по несуществующему id возвращает ошибку")
@allure.severity(allure.severity_level.NORMAL)
def test_patch_missing_id_fails(api: ApiClient) -> None:
    with pytest.raises((AssertionError, requests.HTTPError)):
        api.patch(missing_entity_id(), entity_request())


@allure.title("Повторное удаление уже удалённой сущности возвращает ошибку")
@allure.severity(allure.severity_level.NORMAL)
def test_double_delete_fails(api: ApiClient) -> None:
    entity_id = api.create(entity_request())
    api.delete(entity_id)

    with pytest.raises((AssertionError, requests.HTTPError)):
        api.delete(entity_id)
