"""Фикстуры конфигурации запуска."""
from __future__ import annotations

import os

import pytest

from config.config import AppConfig, load_config
from config.credentials import Credentials, has_credentials, load_credentials


@pytest.fixture(scope="session")
def app_config() -> AppConfig:
    """Конфигурация запуска (одна на всю сессию)."""
    return load_config(os.getenv("APP_CONFIG", "android.local"))


@pytest.fixture(scope="session")
def credentials() -> Credentials | None:
    """Учётные данные для авторизации (MSISDN + код верификации из .env).

    Загружаются для всех тестов; возвращает None, если переменные не заданы.
    Тест сам решает, использовать их или нет: авторизационные сцены проверяют
    credentials на None (и падают с понятной ошибкой вместо позднего
    NoSuchElement), неавторизованные просто не обращаются к ним.
    """
    return load_credentials() if has_credentials() else None
