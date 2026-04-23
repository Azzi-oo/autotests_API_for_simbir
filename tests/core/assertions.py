"""Доменные ассерты.

Тесты не должны повторять одинаковые сравнения поле-за-полем — это шумит
и мешает читать чистый код. Любая проверка, которая используется больше
одного раза, переезжает сюда и получает шаг Allure.
"""
from __future__ import annotations

import allure

from tests.core.models import EntityRequest, EntityResponse


@allure.step("Ответ сервиса соответствует отправленному запросу")
def assert_entity_matches_request(request: EntityRequest, response: EntityResponse) -> None:
    mismatches: list[str] = []
    if response.title != request.title:
        mismatches.append(f"title: expected {request.title!r}, got {response.title!r}")
    if response.verified != request.verified:
        mismatches.append(f"verified: expected {request.verified}, got {response.verified}")
    if response.important_numbers != request.important_numbers:
        mismatches.append(
            f"important_numbers: expected {request.important_numbers}, "
            f"got {response.important_numbers}"
        )
    if response.addition.additional_info != request.addition.additional_info:
        mismatches.append(
            f"addition.additional_info: expected {request.addition.additional_info!r}, "
            f"got {response.addition.additional_info!r}"
        )
    if response.addition.additional_number != request.addition.additional_number:
        mismatches.append(
            f"addition.additional_number: expected {request.addition.additional_number}, "
            f"got {response.addition.additional_number}"
        )
    assert not mismatches, "response diverges from request:\n  - " + "\n  - ".join(mismatches)
