"""Загрузка и валидация конфигурации запуска.

Конфиг выбирается через переменную окружения APP_CONFIG
(например: android.local, ios.local). По умолчанию — android.local.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

CONFIG_DIR = Path(__file__).parent


class AppConfig(BaseModel):
    """Типизированная модель конфигурации Appium-сессии."""

    platform: Literal["android", "ios"]
    automation_name: str  # UiAutomator2 / XCUITest
    app: str  # путь к сборке или remote URL
    platform_version: str = ""
    device_name: str = ""
    udid: str | None = None
    remote_url: str = "http://127.0.0.1:4723"
    # Доп. возможности, общие для обеих платформ
    no_reset: bool = True
    full_reset: bool = False
    new_command_timeout: int = 300
    # Закрывать ли системные permission-диалоги после старта приложения.
    # Имеет смысл включать только если приложение реально показывает диалоги
    # разрешений при запуске — иначе grant_permissions впустую тратит ~50 c
    # на поиск несуществующих кнопок «Разрешить».
    handle_permissions: bool = False


def load_config(name: str | None = None) -> AppConfig:
    """Загружает YAML-конфиг по имени и валидирует через pydantic."""
    name = name or os.getenv("APP_CONFIG", "android.local")
    path = CONFIG_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Конфиг не найден: {path}")
    with path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return AppConfig(**raw)
