"""HTTP-клиент, возвращающий десериализованные модели Pydantic.

Каждый вызов обернут в шаг Allure, поэтому в отчете отображаются тела запроса и ответа,
а не только названия тестов.
"""
from __future__ import annotations

import os

import allure
import requests

from tests.models import (
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
        params: dict[str, object] = {"page": page, "perPage": per_page}
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
            self._attach("response", f"HTTP {response.status_code}")
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
