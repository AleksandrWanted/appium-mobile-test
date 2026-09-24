"""Фикстуры конфигурации запуска."""
from __future__ import annotations

import os

import pytest

from config.config import AppConfig, load_config


@pytest.fixture(scope="session")
def app_config() -> AppConfig:
    """Конфигурация запуска (одна на всю сессию)."""
    return load_config(os.getenv("APP_CONFIG", "android.local"))
