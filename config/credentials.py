"""Учётные данные для тестов с авторизацией.

Читаются из переменных окружения (см. .env / .env.example):
    MSISDN            — тестовый номер телефона (например, «79001234567»)
    VERIFICATION_CODE — код верификации для входа

Отдельная секция, а не поля AppConfig: учётные данные — тестовые данные,
а не параметры Appium-сессии, поэтому без префикса APPIUM_ и без места
в YAML-профилях (секреты в git не хранятся).
"""
from __future__ import annotations

import os

from pydantic import BaseModel, Field


class Credentials(BaseModel):
    """Учётные данные тестового пользователя для авторизации в приложении."""

    msisdn: str = Field(..., min_length=10, description="Номер телефона (MSISDN)")
    verification_code: str = Field(..., min_length=3, description="Код верификации")


def load_credentials() -> Credentials:
    """Собирает учётные данные из переменных окружения MSISDN / VERIFICATION_CODE.

    Бросает понятную ошибку со списком недостающих переменных, если их нет,
    — чтобы тест с авторизацией падал с внятной причиной, а не с поздним
    NoSuchElement на экране логина.
    """
    missing = [name for name in ("MSISDN", "VERIFICATION_CODE") if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            f"Для запуска тестов с авторизацией не заданы переменные окружения: "
            f"{', '.join(missing)}. Добавьте их в .env — см. .env.example."
        )
    return Credentials(
        msisdn=os.environ["MSISDN"].strip(),
        verification_code=os.environ["VERIFICATION_CODE"].strip(),
    )


def has_credentials() -> bool:
    """Заданы ли обе переменные (MSISDN и VERIFICATION_CODE) в окружении."""
    return all(os.getenv(name) for name in ("MSISDN", "VERIFICATION_CODE"))
