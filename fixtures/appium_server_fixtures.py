"""Фикстуры Appium-сервера."""
from __future__ import annotations

from urllib.parse import urlparse

import pytest

from config.config import AppConfig
from fixtures.config_fixtures import app_config
from src.driver.appium_server import ManagedAppiumServer


@pytest.fixture(scope="session")
def appium_server(app_config: AppConfig):
    """Session-фикстура: гарантирует, что локальный Appium-сервер запущен.

    Если {remote_url}/status уже отвечает — сервер внешний (ручной запуск,
    CI-entrypoint), фикстура ничего не поднимает и teardown его не трогает.
    Иначе запускает собственный процесс `appium server` (параметры запуска —
    server_* поля конфига) и останавливает его после сессии.
    Для удалённых хостов (BrowserStack и т.п.) локальный сервер
    не поднимается — по умолчанию предполагается, что он уже работает.
    """
    parsed = urlparse(app_config.remote_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 4723

    manager = ManagedAppiumServer(
        address=host,
        port=port,
        session_override=app_config.server_session_override,
        log_level=app_config.server_log_level,
    )
    started = manager.ensure_running()
    yield manager
    if started:
        manager.stop()
