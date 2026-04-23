"""HTTP-клиент сервиса — транспортный слой.

Каждый вызов обёрнут в шаг Allure, тело запроса и ответа попадают в отчёт.
Типизированные методы возвращают Pydantic-модели, сырые методы (`raw_*`)
используются в негативных тестах, где нужен контроль над статусом и телом.
"""
from __future__ import annotations

import os
from typing import Any

import allure
import requests

from tests.core.models import (
    EntityListResponse,
    EntityRequest,
    EntityResponse,
)

DEFAULT_BASE_URL = "http://localhost:8080"


class ApiClient:
    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = (base_url or os.environ.get("BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    @staticmethod
    def _attach(name: str, body: str) -> None:
        allure.attach(body, name=name, attachment_type=allure.attachment_type.TEXT)

    def create(self, entity: EntityRequest) -> int:
        with allure.step(f"POST /api/create title={entity.title!r}"):
            payload = entity.model_dump()
            self._attach("request", str(payload))
            response = self.session.post(
                self._url("/api/create"), json=payload, timeout=self.timeout
            )
            self._attach("response", f"HTTP {response.status_code}\n{response.text}")
            response.raise_for_status()
            return int(response.text.strip())

    def get(self, entity_id: int) -> EntityResponse:
        with allure.step(f"GET /api/get/{entity_id}"):
            response = self.session.get(self._url(f"/api/get/{entity_id}"), timeout=self.timeout)
            self._attach("response", f"HTTP {response.status_code}\n{response.text}")
            response.raise_for_status()
            return EntityResponse.model_validate(response.json())

    def get_all(
        self,
        *,
        page: int = 1,
        per_page: int = 50,
        title: str | None = None,
        verified: bool | None = None,
    ) -> EntityListResponse:
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        if title is not None:
            params["title"] = title
        if verified is not None:
            params["verified"] = str(verified).lower()
        with allure.step(f"GET /api/getAll params={params}"):
            response = self.session.get(
                self._url("/api/getAll"), params=params, timeout=self.timeout
            )
            self._attach("response", f"HTTP {response.status_code}\n{response.text}")
            response.raise_for_status()
            return EntityListResponse.model_validate(response.json())

    def patch(self, entity_id: int, entity: EntityRequest) -> None:
        with allure.step(f"PATCH /api/patch/{entity_id}"):
            payload = entity.model_dump()
            self._attach("request", str(payload))
            response = self.session.patch(
                self._url(f"/api/patch/{entity_id}"), json=payload, timeout=self.timeout
            )
            self._attach("response", f"HTTP {response.status_code}\n{response.text}")
            assert response.status_code == 204, (
                f"expected 204, got {response.status_code}: {response.text}"
            )

    def delete(self, entity_id: int) -> None:
        with allure.step(f"DELETE /api/delete/{entity_id}"):
            response = self.session.delete(
                self._url(f"/api/delete/{entity_id}"), timeout=self.timeout
            )
            self._attach("response", f"HTTP {response.status_code}")
            assert response.status_code == 204, (
                f"expected 204, got {response.status_code}: {response.text}"
            )

    def raw_get(self, path: str) -> requests.Response:
        with allure.step(f"GET {path} (raw)"):
            response = self.session.get(self._url(path), timeout=self.timeout)
            self._attach("response", f"HTTP {response.status_code}\n{response.text}")
            return response

    def raw_delete(self, path: str) -> requests.Response:
        with allure.step(f"DELETE {path} (raw)"):
            response = self.session.delete(self._url(path), timeout=self.timeout)
            self._attach("response", f"HTTP {response.status_code}\n{response.text}")
            return response

    def raw_patch(self, path: str, json_body: Any) -> requests.Response:
        with allure.step(f"PATCH {path} (raw)"):
            self._attach("request", str(json_body))
            response = self.session.patch(self._url(path), json=json_body, timeout=self.timeout)
            self._attach("response", f"HTTP {response.status_code}\n{response.text}")
            return response

    def raw_post(self, path: str, json_body: Any) -> requests.Response:
        with allure.step(f"POST {path} (raw)"):
            self._attach("request", str(json_body))
            response = self.session.post(self._url(path), json=json_body, timeout=self.timeout)
            self._attach("response", f"HTTP {response.status_code}\n{response.text}")
            return response
