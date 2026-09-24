"""Загрузка и валидация конфигурации запуска.

Конфиг выбирается через переменную окружения APP_CONFIG
(например: android.local, ios.local). По умолчанию — android.local.

Отдельные поля можно переопределить переменными APPIUM_<ПОЛЕ>
(APPIUM_UDID, APPIUM_REMOTE_URL, ...) — удобно для CI/облачных запусков,
не трогая YAML-профили. Приоритет: APPIUM_* > YAML > дефолты AppConfig.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

# YAML-профили лежат в configs/ рядом с python-пакетом config/ (модуль config.py)
CONFIG_DIR = Path(__file__).parent.parent / "configs"


class AppConfig(BaseModel):
    """Типизированная модель конфигурации Appium-сессии."""

    platform: Literal["android", "ios"]
    app: str  # путь к сборке или remote URL
    platform_version: str = ""
    device_name: str = ""
    udid: str | None = None
    remote_url: str = "http://127.0.0.1:4723"
    # Доп. возможности, общие для обеих платформ
    no_reset: bool = True
    full_reset: bool = False
    new_command_timeout: int = 300
    # Предотвращать системные permission-диалоги: Appium сам выдаёт все
    # RUNTIME-разрешения (Android — pm grant при установке APK + прямой грант
    # в фикстуре; iOS — autoAcceptAlerts: WDA тапает «Разрешить»/Allow на
    # нативном alert). Диалог не появится ни при первом запуске, ни после
    # рестартов. Выключить имеет смысл только тестам, которые проверяют сами
    # диалоги, — закрыть показанный тогда можно pages.common.grant_permissions().
    auto_grant_permissions: bool = False
    # Параметры сервера `appium server`, поднимаемого фикстурой
    # (на внешний сервер из remote_url не влияют). session_override:
    # при новом createSession убивать зависшую сессию того же клиента —
    # лечит ошибки проксирования после прерванного прогона.
    server_session_override: bool = False
    server_log_level: str = "info"


def _env_overrides() -> dict[str, str]:
    """Переменные APPIUM_<ПОЛЕ> перебивают одноимённые поля YAML-конфига.

    Имена переменных строятся из полей AppConfig (APPIUM_UDID, APPIUM_REMOTE_URL
    и т.д.). Типы приводить не нужно — pydantic сам сделает '300' → int,
    'true' → bool при валидации модели.
    """
    overrides = {}
    for field in AppConfig.model_fields:
        value = os.getenv(f"APPIUM_{field.upper()}")
        if value:
            overrides[field] = value
    return overrides


def load_config(name: str | None = None) -> AppConfig:
    """Загружает YAML-конфиг по имени и валидирует через pydantic.

    Приоритет полей: переменные APPIUM_* > значения YAML > дефолты AppConfig.
    YAML-файл может отсутствовать — тогда конфиг собирается только из
    переменных окружения (удобно для CI/облачных запусков без профилей).
    """
    name = name or os.getenv("APP_CONFIG", "android.local")
    path = CONFIG_DIR / f"{name}.yaml"

    raw: dict = {}
    if path.exists():
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    raw.update(_env_overrides())
    if not raw:  # нет ни YAML, ни env-переменных — как раньше, понятная ошибка
        raise FileNotFoundError(f"Конфиг не найден: {path} (и APPIUM_* не заданы)")
    return AppConfig(**raw)
