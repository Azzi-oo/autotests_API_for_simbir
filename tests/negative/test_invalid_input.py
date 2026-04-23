"""Negative: некорректные входные данные."""
from __future__ import annotations

import allure
import pytest

from tests.core.api_client import ApiClient

pytestmark = [
    pytest.mark.api,
    pytest.mark.negative,
    allure.epic("Entity API"),
    allure.story("Invalid input"),
]


@allure.title("GET с нечисловым id возвращает 4xx")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.parametrize("bad_id", ["abc", "-1", "1.5", "%20"])
def test_get_with_non_numeric_id(api: ApiClient, bad_id: str) -> None:
    response = api.raw_get(f"/api/get/{bad_id}")
    assert response.status_code >= 400


@allure.title("POST /api/create без обязательного поля title возвращает ошибку")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_without_title_fails(api: ApiClient) -> None:
    response = api.raw_post(
        "/api/create",
        {
            "verified": True,
            "addition": {"additional_info": "x", "additional_number": 1},
            "important_numbers": [1],
        },
    )
    assert response.status_code >= 400


@allure.title("POST /api/create без обязательного поля verified возвращает ошибку")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_without_verified_fails(api: ApiClient) -> None:
    response = api.raw_post(
        "/api/create",
        {
            "title": "only-title",
            "addition": {"additional_info": "x", "additional_number": 1},
            "important_numbers": [1],
        },
    )
    assert response.status_code >= 400


@allure.title("GET /api/getAll с нечисловым verified возвращает 400")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.parametrize("bad_verified", ["maybe", "2", "yes"])
def test_get_all_with_invalid_verified(api: ApiClient, bad_verified: str) -> None:
    response = api.raw_get(f"/api/getAll?verified={bad_verified}")
    assert response.status_code == 400
